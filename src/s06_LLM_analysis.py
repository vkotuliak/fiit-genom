import transformers
import torch

from s05_data_preparation import aggregate_data


def analyze_text_with_llm(text):
    # model_id = "openai/gpt-oss-20b"
    # model_id = "meta-llama/Llama-3.3-70B-Instruct" # Too big, requires more resources
    model_id = "Qwen/Qwen2.5-7B"

    pipeline = transformers.pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )

    prompt = f"""
    Text: {text}
    Please analyze the text above and provide a detailed summary of its content, focusing on the main themes, findings, and implications.
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
    variation_id = 569
    data = aggregate_data(variation_id)
    analysis_results = analyze_text_with_llm(data)
    print("Analysis Results:")
    print(analysis_results)


if __name__ == "__main__":
    main()
