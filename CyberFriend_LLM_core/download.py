from modelscope import snapshot_download
model_dir = snapshot_download("ZhipuAI/chatglm3-6b", cache_dir='./', revision = "v1.0.0")