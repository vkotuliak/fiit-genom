from transformers import pipeline
import transformers
import torch

from s05_data_preparation import aggregate_data


def analyze_text_with_llm(text):
    model_id = "/home/kotuliakv/.llama/checkpoints/Llama3.3-70B-Instruct"

    pipeline = transformers.pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.float16},
        device_map="auto",
    )

    prompt = f"""
    Perform the following analysis on the provided text:
    1. Identify the main topic of the text.
    2. Summarize the key points.
    3. Provide any relevant insights or conclusions.

    Text: {text}
    """

    response = pipeline(prompt, max_new_tokens=256)
    analysis = response[0]["generated_text"]

    return analysis


def main():
    variation_id = 69
    data = aggregate_data(variation_id)
    print(data)
    analysis_results = analyze_text_with_llm(data)
    print("Analysis Results:")
    print(analysis_results)


if __name__ == "__main__":
    main()
