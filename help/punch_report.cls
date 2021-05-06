% This document class provides a simple memo for LaTeX users.
% It is based on article.cls and inherits most of the functionality
% that class.
% 
% Author: Rob Oakes, Copyright 2010.  Released under the LGPL, version 3.
% A copy of the LGPL can be found at http://www.gnu.org/licenses/lgpl.html

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{punch_report}[2010/07/31 - Simple Report Class, Including Logo]
\RequirePackage{palatino}
\RequirePackage{fancyhdr}
\RequirePackage{geometry}
\RequirePackage{lastpage}
\RequirePackage{svg}

\newcommand{\revision}{0.0}
\newcommand{\reportLogo}{\includesvg[height=10mm]{figures/punch}}
%%\newcommand{\reportLogo}{\includesvg{xc_report_logo}}

% Load the Base Class
\LoadClassWithOptions{article}
\usepackage{geometry}
\geometry{hmargin={2.5cm,1.5cm},vmargin={3cm,3cm}}

\pagestyle{fancy}
\fancypagestyle{plain}{
\fancyhf{} %anula los valores de fancy por defecto 

\fancyfoot[LE]{صفحه \thepage\ از \pageref{LastPage}}
\fancyfoot[CE]{\reportLogo}
% \fancyfoot[RE]{\emph{rev. \revision}}

\fancyfoot[LO]{\emph{\date}}
\fancyfoot[CO]{\reportLogo}
\fancyfoot[RO]{صفحه \thepage\ از \pageref{LastPage}}
\renewcommand{\headrulewidth}{0pt} %Dibuja una raya debajo de la cabecera
\renewcommand{\footrulewidth}{0pt}
}

\renewcommand{\headrulewidth}{0pt} %Dibuja una raya debajo de la cabecera
\renewcommand{\footrulewidth}{0pt}
% \textheight= 22cm %%Espacio vertical para el texto.
%\textwidth=16cm
\marginparwidth=2mm

\fancyhf{} %anula los valores de fancy por defecto 

\fancyhead[LE]{\textsc{\karfarma}}
\fancyhead[RO]{\leftmark}
\fancyhead[RO]{\textsc{\rightmark}}

\fancyfoot[LE]{صفحه \thepage\ از \pageref{LastPage}}
\fancyfoot[CE]{\reportLogo}
% \fancyfoot[RE]{\emph{rev. \revision}}

\fancyfoot[LO]{\emph{\date}}
\fancyfoot[CO]{\reportLogo}
\fancyfoot[RO]{صفحه \thepage\ از \pageref{LastPage}}

\newcommand{\developer}{ابراهیم رعیت رکن آبادی}



