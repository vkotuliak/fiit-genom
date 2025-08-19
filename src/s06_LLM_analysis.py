import transformers
# from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import os
import torch
from transformers import BitsAndBytesConfig

from s05_data_preparation import aggregate_data


def analyze_text_with_llm(text):
    # model_id = "openai/gpt-oss-20b"
    # model_id = "meta-llama/Llama-3.3-70B-Instruct" # Too big, requires more resources
    # model_id = "Qwen/Qwen2.5-7B"
    model_id = "Qwen/Qwen2.5-72B-Instruct"

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    pipeline = transformers.pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16, "quantization_config": quantization_config},
        device_map="auto",
    )

    prompt = f"""
    Text: {text}
    Please analyze the text above and tell me if the genetic variant is pathogenic, likely pathogenic, uncertain significance, likely benign, or benign.
    Provide a brief explanation for your classification.
    """

    """
    Past prompts:
    Please analyze the text above and give me 3 main points what is the text about. 
    """

    response = pipeline(prompt, max_new_tokens=512, num_return_sequences=1)
    # print(f"response: {response}")
    analysis = response[0]["generated_text"][len(prompt) :]
    # print(f"Analysis Length: {len(analysis)}")

    if model_id == "openai/gpt-oss-20b":
        keyword = ".assistantfinal"
        analysis = analysis[analysis.find(keyword) + len(keyword) :].strip()

    return analysis


def main():
    variation_id = 74
    data = aggregate_data(variation_id)
    analysis_results = analyze_text_with_llm(data)
    print("Analysis Results:")
    print(analysis_results)


if __name__ == "__main__":
    main()
