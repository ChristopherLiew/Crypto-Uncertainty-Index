"""
Gradio demo app with Fine Tuned Hedge Classifier
"""

import gradio as gr
from transformers import pipeline
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

# Config
MODEL_CHECKPOINT = "nlp/hedge_classifier/models/best_pbt_bertweet/checkpoint"
MODEL_NAME = "vinai/bertweet-base"

# Pipeline for Inference
tokenizer_kwargs = {
    "padding": True,
    "truncation": True,
}
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, normalization=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_CHECKPOINT)
pipe = pipeline("text-classification", model=model, tokenizer=tokenizer)


def predict(text):
    return pipeline(text, **tokenizer_kwargs)[0]


iface = gr.Interface(
    fn=predict,
    inputs="text",
    outputs="text",
    examples=[["I'm not too sure if we should hodl BTC ..."]],
)


def run_app():
    iface.launch()
