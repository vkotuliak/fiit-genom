import transformers
# from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import os
import torch
from transformers import BitsAndBytesConfig

from s05_data_preparation import aggregate_data


def analyze_text_with_llm(text):
    # model_id = "openai/gpt-oss-20b"
    model_id = "meta-llama/Llama-3.3-70B-Instruct" # Too big, requires more resources
    # model_id = "Qwen/Qwen2.5-7B"
    # model_id = "Qwen/Qwen2.5-72B-Instruct"

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

    # 1. Split the text into manageable chunks
    chunk_size = 50000
    text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    # 2. Map Step: Process all chunks in a single batch for efficiency
    print(f"Processing {len(text_chunks)} chunks in a batch...")
    
    summary_prompts = [f"""
    ### Instruction:
    You are a research assistant. Read the following text excerpt from a collection of academic papers and summarize the key findings or main points.

    ### Input Text:
    {chunk}

    ### Response:
    """ for chunk in text_chunks]

    responses = pipeline(summary_prompts, max_new_tokens=256, num_return_sequences=1)

    summaries = []
    for i, response in enumerate(responses):
        prompt = summary_prompts[i]
        summary = response[0]["generated_text"][len(prompt):].strip()
        summaries.append(summary)

    # 3. Reduce Step: Synthesize the summaries
    print("Synthesizing final themes...")
    combined_summaries = "\n\n---\n\n".join(summaries)

    final_prompt = f"""
    ### Instruction:
    You are a research assistant. Read the text provided below, which contains summaries from several academic papers. Your task is to synthesize the content and identify the three most significant, overarching themes. List these themes concisely.

    ### Input Text:
    {combined_summaries}

    ### Response:
    """

    response = pipeline(final_prompt, max_new_tokens=512, num_return_sequences=1)
    analysis = response[0]["generated_text"][len(final_prompt) :]

    if model_id == "openai/gpt-oss-20b":
        keyword = ".assistantfinal"
        analysis = analysis[analysis.find(keyword) + len(keyword) :].strip()

    return analysis


def main():
    variation_id = 3254
    data = aggregate_data(variation_id)
    analysis_results = analyze_text_with_llm(data)
    print("Analysis Results:")
    print(analysis_results)


if __name__ == "__main__":
    main()
