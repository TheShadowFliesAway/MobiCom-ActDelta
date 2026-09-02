%% ===================================================================
%%  _offline/acmart.cls  --  FALLBACK ONLY. NOT for submission.
%%
%%  A minimal stand-in that approximates ACM sigconf geometry (two columns,
%%  9/10 pt, 7.0 in text width, 3.335 in columns) so the document can be
%%  compiled and proofread on a machine without the real acmart bundle.
%%
%%  It is loaded ONLY by `make offline`, which prepends this directory to
%%  TEXINPUTS. A normal `make` uses the real acmart from your TeX
%%  distribution or Overleaf. Line breaks, float placement and the
%%  reference format will differ slightly from the real class -- always
%%  check page count against a real acmart build before submitting.
%% ===================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{acmart}[2026/01/01 offline sigconf stand-in]

\newif\ifacm@anon \acm@anonfalse
\DeclareOption{anonymous}{\acm@anontrue}
\DeclareOption{sigconf}{}
\DeclareOption{review}{}
\DeclareOption{nonacm}{}
\DeclareOption{screen}{}
\DeclareOption*{}
\ProcessOptions\relax

\LoadClass[9pt,twocolumn,letterpaper]{extarticle}

\RequirePackage[letterpaper,top=0.75in,bottom=1.0in,left=0.75in,right=0.75in,
                columnsep=0.33in]{geometry}
\RequirePackage{times}
\RequirePackage{caption}
\RequirePackage{natbib}
\RequirePackage{lineno}

\setlength{\parindent}{9pt}
\setlength{\emergencystretch}{2em}
\bibliographystyle{plainnat}
\setcitestyle{numbers,square,comma}

% --- headings, close to acmart's proportions
\RequirePackage{titlesec}
\titleformat{\section}{\normalfont\large\bfseries}{\thesection}{0.6em}{}
\titleformat{\subsection}{\normalfont\normalsize\bfseries}{\thesubsection}{0.6em}{}
\titleformat{\subsubsection}{\normalfont\normalsize\itshape}{\thesubsubsection}{0.6em}{}
\titlespacing*{\section}{0pt}{8pt plus 2pt minus 2pt}{3pt}
\titlespacing*{\subsection}{0pt}{6pt plus 2pt minus 2pt}{2pt}

\captionsetup{font=small,labelfont=bf,labelsep=colon,skip=4pt}

% --- title block
\newcommand{\subtitle}[1]{\gdef\@subtitle{#1}}
\gdef\@subtitle{}
\renewcommand{\maketitle}{%
  \twocolumn[%
    \begin{@twocolumnfalse}
    \begin{center}
      {\LARGE\bfseries\@title\par}\vspace{4pt}
      \ifx\@subtitle\@empty\else{\large\@subtitle\par}\vspace{6pt}\fi
      {\normalsize\ifacm@anon Anonymous Author(s)\else\@author\fi\par}
    \end{center}\vspace{8pt}
    \begin{quotation}\noindent\ignorespaces\@abstractcontent\end{quotation}
    \ifx\@keywordscontent\@empty\else
      \vspace{3pt}\noindent{\small\textbf{Keywords:} \@keywordscontent\par}\fi
    \vspace{10pt}
    \end{@twocolumnfalse}]%
}

\gdef\@abstractcontent{}
\gdef\@keywordscontent{}
\renewenvironment{abstract}{\global\setbox0\vbox\bgroup\hsize\textwidth
  \def\@currenvir{abstract}}{\egroup}
\long\def\abstract#1\endabstract{}
% capture the abstract body verbatim-ish
\RequirePackage{environ}
\RenewEnviron{abstract}{\global\let\@abstractcontent\BODY}
\newcommand{\keywords}[1]{\gdef\@keywordscontent{#1}}

% --- CCS boilerplate becomes a no-op
\RequirePackage{verbatim}
\newenvironment{CCSXML}{\comment}{\endcomment}
\newcommand{\ccsdesc}[2][]{}
\newcommand{\acmConference}[4]{}
\newcommand{\acmYear}[1]{}
\newcommand{\acmDOI}[1]{}
\newcommand{\acmISBN}[1]{}
\newcommand{\copyrightyear}[1]{}
\newcommand{\settopmatter}[1]{}
\newcommand{\received}[2][]{}
\newcommand{\orcid}[1]{}
\newcommand{\affiliation}[2][]{}
\newcommand{\institution}[1]{#1}
\newcommand{\city}[1]{#1}
\newcommand{\country}[1]{#1}
\newcommand{\email}[1]{#1}
\endinput
