import dspy
from pydantic import BaseModel, Field
from typer import Typer

from dspygen.modules.gen_pydantic_instance_module import gen_pydantic_instance_call
from dspygen.modules.source_code_pep8_docs_module import source_code_docs_call
from dspygen.utils.dspy_tools import init_dspy
from typetemp.functional import render

app = Typer()


class DSPyModuleTemplate(BaseModel):
    """{{ inputs }} -> {{ outputs }}"""
    inputs: list[str] = Field(..., description="Inputs for dspy.Module jinja template.")
    output: str = Field(..., description="Output for dspy.Module jinja template.")
    class_name: str = Field(..., description="Class name combining the inputs and outputs")


dspy_module_template = '''"""
{{ docstring }}
"""
import dspy
from typer import Typer
from dspygen.utils.dspy_tools import init_dspy


app = Typer()


{%- set module_name = model.class_name | class_name ~ "Module" %}
{%- set inputs_join = model.inputs | join(', ') %}    
{%- set inputs_join_kwargs = model.inputs | map('to_kwarg') | join(', ') %}        
{% set var_name = model.class_name | var_name %}


class {{ module_name }}(dspy.Module):
    """{{ module_name }}"""

    def forward(self, {{ inputs_join }}):
        pred = dspy.Predict("{{ inputs_join }} -> {{ model.output }}")
        result = pred({{ inputs_join_kwargs }}).{{ model.output }}
        return result


def {{ var_name }}_call({{ inputs_join }}):
    {{ var_name }} = {{ module_name }}()
    return {{ var_name }}.forward({{ inputs_join_kwargs }})


@app.command()
def call({{ inputs_join }}):
    """{{ module_name }}"""
    init_dspy()
    
    print({{ var_name }}_call({{ inputs_join_kwargs }}))


def main():
    init_dspy()
{% for input in model.inputs %}
    {{ input }} = ""
{% endfor %}
    print({{ var_name }}_call({{ inputs_join_kwargs }}))


if __name__ == "__main__":
    main()

'''


class SignatureDspyModuleModule(dspy.Module):
    """SignatureDspyModuleModule"""

    def forward(self, signature):
        tmpl_model = gen_pydantic_instance_call(signature, DSPyModuleTemplate)

        source = render(dspy_module_template, model=tmpl_model, docstring="")

        docs = source_code_docs_call(source)

        source = render(dspy_module_template, model=tmpl_model, docstring=docs)

        return source


def gen_dspy_module_call(signature):
    signature_dspy_module = SignatureDspyModuleModule()
    return signature_dspy_module.forward(signature=signature)
 

@app.command()
def call(signature):
    """SignatureDspyModuleModule"""
    init_dspy()

    print(gen_dspy_module_call(signature=signature))
    
    
def main():
    init_dspy()

    signature = "subject -> newsletter_article"
    print(gen_dspy_module_call(signature=signature))


if __name__ == "__main__":
    main()