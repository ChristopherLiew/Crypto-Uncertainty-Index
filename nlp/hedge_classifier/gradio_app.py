"""
Gradio demo / eval app for Fine Tuned Hedge Classifier
"""

import shap
import gradio as gr
from typing import Any, Dict, Tuple, Optional
from transformers import pipeline
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)
from utils.logger import log


def run(
    hf_model_name: str = "vinai/bertweet-base",
    model_save_dir: Optional[str] = None,
    theme: str = "dark-peach",
) -> None:

    # Pipeline for Inference
    log.info("Loading Hugging Face Model & Tokenizer ...")
    tokenizer = AutoTokenizer.from_pretrained(hf_model_name, normalization=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        hf_model_name if model_save_dir is None else model_save_dir
    )

    log.info("Constructing Pipeline")
    pipe = pipeline("text-classification", model=model, tokenizer=tokenizer)
    tokenizer_kwargs = {
        "padding": True,
        "truncation": True,
    }

    # Predict Function
    def predict(text) -> Tuple[Dict[str, float], Any]:

        res = pipe(text, **tokenizer_kwargs, return_all_scores=True)[0]
        pred = sorted(res, key=lambda x: x.get("score"), reverse=True)
        explainer = shap.Explainer(pipe)
        shap_values = explainer([text])

        tidied_labels = {}
        for i in pred:
            label, score = i.get("label", None), i.get("score", None)
            label = "Hedged" if label == "LABEL_1" else "Not Hedged"
            tidied_labels[label] = score

        pred_class = pred[0].get("label", None)
        html_explainer = shap.plots.text(shap_values[:, :, pred_class], display=False)
        return tidied_labels, html_explainer

    # Interface
    iface = gr.Interface(
        fn=predict,
        title="Hedge Detection with BERTweet 🤗",
        inputs=gr.inputs.Textbox(
            lines=30,
            label="Give me some text",
            placeholder="I am possibly a hedged sentence ...",
        ),
        outputs=[
            # gr.outputs.Textbox(label="Is it Hedged?"),
            gr.outputs.Label(num_top_classes=2, label="Result"),
            gr.outputs.HTML(label="SHAPley Explained"),
        ],
        examples=[
            ["BTC will probably hit 100k in by May 🚀🚀🚀"],
            ["🐋  may be dumping coins before the fork"],
        ],
        theme=theme,
    )

    print("Launching Gradio app ...")
    app, local_url, share_url = iface.launch(inbrowser=True, share=False, debug=False)
