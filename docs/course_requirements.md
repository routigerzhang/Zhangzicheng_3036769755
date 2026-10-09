# Course requirements and submission format

## What kind of project this is

This is an AI-assisted empirical paper replication project in applied labor
economics. The project reconstructs the data and empirical design of Card and
Krueger (1994), who used a difference-in-differences comparison of New Jersey
and eastern Pennsylvania restaurants around New Jersey's 1992 minimum-wage
increase. It is not a purely theoretical essay or a machine-learning project:
the main deliverables are data construction, econometric replication,
validation, interpretation, reproducible code, and one independent empirical
extension.

## Requirements confirmed from the supplied course materials

### Empirical report

The report should contain:

- the research question and motivation;
- data sources, sample construction, and variable definitions;
- the empirical design;
- core replication results and comparison with the original paper;
- one independent extension;
- validation, limitations, and conclusion.

For this paper option, the assigned core outputs are Tables 2-4 and Figure 1.
Table 1 is not required because the necessary data are restricted.

### Reproducibility package

The package should contain:

- raw data or clear instructions for accessing restricted data;
- processed data used in the final analysis, when redistribution is permitted;
- complete Python, Stata, or R code;
- a README explaining reproduction;
- an accessible GitHub repository URL;
- meaningful Git commit history rather than one final upload;
- a reusable workflow or skill that generates the main tables and figures.

After the documented input data are placed in the input folder, the workflow
should generate the main tables and figures without manual modification of the
data or code.

### AI-use disclosure

The submission should explain:

- where and how AI was used;
- how AI-generated code, analysis, and writing were checked;
- important AI errors or suggestions that were corrected or rejected.

The project includes a completed disclosure draft at
`docs/ai_use_disclosure.md`.

### Additional requirements

- The assigned core table or figure must be replicated.
- Every project must include one independent extension answering a clearly
  defined economic question.
- A replication does not need to match every number in the original paper, but
  differences must be explained by data coverage, sample period, or
  implementation choices.
- Licensed, confidential, or otherwise restricted data must not be uploaded to
  GitHub.

## Requirements visible in the supplied grading slide

The supplied grading slide lists these evaluation dimensions and weights:

- Understanding of the paper and research design: 5%;
- Data and variable construction: 25%;
- Core replication and validation: 25%;
- Independent extension: 20%;
- Reproducibility and workflow: 20%.

The slide emphasizes that the extension is judged by the clarity of the
economic question, empirical design, validation, and insight, not by the
amount of code alone.

## Items not specified in the supplied materials

The files and screenshots provided for this project do not state a definitive
word limit, required filename, required PDF or Word format, or submission
deadline. These details should be confirmed from the course portal or the
instructor before uploading the final package. The project contains both an
editable DOCX report and a PDF report so either format can be selected if the
course permits both.
