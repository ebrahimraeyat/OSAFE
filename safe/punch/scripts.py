import FreeCAD, Part
import FreeCADGui as Gui

def get_intersection(obj1, obj2):
  '''
  return intersection faces that common in obj1 and obj2
  '''
  outer = obj1.Shape.cut(obj2.Shape)
  inner = obj1.Shape.common(obj2.Shape)
  faces_outer = outer.Faces
  faces_inner = inner.Faces

  intersection_faces = []
  for fo in faces_outer:
    for fi in faces_inner:
      if -0.01 < fo.Area - fi.Area < .01:
        # print( 'Face Area is equal')
        if len(fo.Vertexes) == len(fi.Vertexes):
          no_same_V = 0
          for vo in fo.Vertexes:
            for vi in fi.Vertexes:
              if -.01 < vo.X -  vi.X < .01 and -.01 < vo.Y - vi.Y < .01 and -.01 < vo.Z - vi.Z < .01:
                no_same_V = no_same_V + 1
                # print 'Found identical Vertex ', no_same_V, ' of ', len(fo.Vertexes), ' Vertexes'
            if  no_same_V == len(fo.Vertexes):
              # print 'All (', no_same_V, ') Vertexes of the two faces are identical'
              intersection_faces.append(fo)

  return intersection_faces 


# sh = Part.makeShell(intersection_faces)
# Part.show(sh)


