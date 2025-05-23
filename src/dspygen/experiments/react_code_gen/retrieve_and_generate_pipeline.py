import os

import inflection
from slugify import slugify

from dspygen.llm_pipe.dsl_pipeline_executor import execute_pipeline


def feature_code_generation():

    context = execute_pipeline(f'{os.getcwd()}/data_gherkin_pipeline.yaml',
                               init_ctx={"file_path": f"{os.getcwd()}/features.csv"})

    file_name = "hello-world"  # slugify(f"{inflection.underscore(result['FeatureDescription'])}")

    with open(f"{file_name}.tsx", 'w') as f:
        code = context.react_code
        # remove trailing ``` if present
        if code.endswith("```"):
            code = code[:-3]
        f.write(context.react_code)
        print(f"React JSX code written to {file_name}")


def main():
    feature_code_generation()


if __name__ == '__main__':
    main()
