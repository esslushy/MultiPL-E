from datasets import load_dataset
from nltk.translate.bleu_score import sentence_bleu
from argparse import ArgumentParser
import numpy as np
import re
from pathlib import Path

def main():
    args = ArgumentParser()
    args.add_argument("--completions", help="Which completions to generate BLEU score for", type=str, required=True)
    args.add_argument("--csv", type=Path, help="Stores results in a csv file")
    args.add_argument("--compute-mean", action="store_true", help="Computes the mean across all problems")
    args = args.parse_args()

    true_dataset = load_dataset("openai_humaneval")
    pred_dataset = load_dataset("bigcode/MultiPL-E-completions", split=f"humaneval.py.{args.completions}.0.2.reworded")

    problem_to_canonical_solution = {re.findall(r'\d+', task_id)[0]: cannonical for task_id, cannonical in zip(true_dataset["test"]["task_id"], true_dataset["test"]["canonical_solution"])}
    problem_to_completions = {problem: completions for problem, completions in  zip(pred_dataset["problem"], pred_dataset["completions"])}

    problem_to_bleu_scores = {}

    for problem in problem_to_completions.keys():
        problem_to_bleu_scores[problem] = []
        for completion in problem_to_completions[problem]:
            problem_to_bleu_scores[problem].append(sentence_bleu([problem_to_canonical_solution[re.findall(r'\d+', problem)[0]].split(" ")], completion.split(" ")))
        problem_to_bleu_scores[problem] = np.max(problem_to_bleu_scores[problem])

    if args.csv:
        with open(args.csv, "wt+") as f:
            f.write("Problem,BLEU\n")
            f.writelines([f"{problem},{score}\n" for problem, score in zip(problem_to_bleu_scores.keys(), problem_to_bleu_scores.values())])
    else:
        print("Problem,BLEU")
        [print(f"{problem},{score}") for problem, score in zip(problem_to_bleu_scores.keys(), problem_to_bleu_scores.values())]

    if args.compute_mean:
        print(f"Mean BLEU Score across all problems: {np.mean(list(problem_to_bleu_scores.values()))}")

if __name__ == "__main__":
    main()