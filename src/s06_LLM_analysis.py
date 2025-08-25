import transformers
# from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import os
import torch
from transformers import BitsAndBytesConfig

from s05_data_preparation import aggregate_data


def analyze_text_with_llm(text):
    # model_id = "Qwen/Qwen3-4B"
    model_id = "Qwen/Qwen2.5-7B"
    # model_id = "openai/gpt-oss-20b"
    # model_id = "meta-llama/Llama-3.3-70B-Instruct" # Too big, requires more resources
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
    # chunk_size = 500000
    # text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    text_chunks = text.split("#####")
    text_chunks = [chunk.strip() for chunk in text_chunks if chunk.strip()]
    # Count characters per chunk
    for i, chunk in enumerate(text_chunks):
        char_count = len(chunk)
        print(f"Chunk {i+1}: {char_count} characters")
    
    # 2. Map Step: Process all chunks in a single batch for efficiency
    print(f"Processing {len(text_chunks)} chunks in a batch...")
    
    summary_prompts = [f"""
    ### Instruction:
    Read the text bellow. State only the number of participants in the scientific paper and nothing more. If it is paper without participants list NA.

    ### Input Text:
    {chunk}

    ### Response:
    """ for chunk in text_chunks]
    # summary_prompts = [f"""
    # Objective: Analyze the following text chunk and extract all information related to the sample size (number of patients) of studies that investigate the link between pathogenic DNA variants and diseases, especially cancer.

    # Instructions:
    # From the text provided below, please identify and list the following details:

    # Specific Numbers: Any mention of the number of patients, participants, subjects, cases, or controls in a study.

    # Context of the Study: The study must be about a demonstrated link between a DNA variant (or mutation) and a disease. Note if the disease is specified as oncological/cancer.

    # Qualitative Descriptions: Extract any descriptive terms for sample size, such as "small cohorts," "large-scale studies," "family studies," or "population-based studies."

    # Averages or Ranges: If the text mentions an average sample size, or a typical range of patient numbers for such studies, extract that information.

    # Output Format:
    # Present the extracted information as a concise list. If no relevant information is found in this chunk, please state: "No relevant information found in this chunk."

    # Input text:
    # {chunk}

    # ### Response:
    # """ for chunk in text_chunks]

    responses = pipeline(summary_prompts, max_new_tokens=256, num_return_sequences=1)

    summaries = []
    for i, response in enumerate(responses):
        prompt = summary_prompts[i]
        summary = response[0]["generated_text"][len(prompt):].strip()
        print(f"Summary for chunk {i+1}: {summary}")
        summaries.append(summary)

    # 3. Reduce Step: Synthesize the summaries
    print("Synthesizing final themes...")
    combined_summaries = "\n\n---\n\n".join(summaries)

    final_prompt = f"""
    ### Instruction:
    Read the text provided below. List only the number of participants in each paper. If it isn't study with participants list NA.

    ### Input Text:
    {combined_summaries}

    ### Response:
    Paper 1:
    Paper 2:
    ...
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
