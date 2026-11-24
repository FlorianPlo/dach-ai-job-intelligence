"""Canonical skill spellings, applied in code at ingest time (so the LLM doesn't have to be
perfect and counts never split across variants). Extend ALIASES when a report shows a split.
Keys are matched case-insensitively after trimming; values are the canonical form."""
import re

ALIASES = {
    # languages
    "python": "Python", "python3": "Python", "py": "Python", "sql": "SQL", "r": "R", "scala": "Scala",
    "java": "Java", "c++": "C++", "cpp": "C++", "c#": "C#", "go": "Go", "golang": "Go", "rust": "Rust",
    "julia": "Julia", "bash": "Bash", "shell": "Bash", "shell scripting": "Bash", "typescript": "TypeScript",
    "javascript": "JavaScript", "matlab": "MATLAB", "sas": "SAS",
    # ML frameworks
    "sklearn": "scikit-learn", "scikit learn": "scikit-learn", "scikit-learn": "scikit-learn",
    "pytorch": "PyTorch", "torch": "PyTorch", "tensorflow": "TensorFlow", "tf": "TensorFlow", "keras": "Keras",
    "jax": "JAX", "xgboost": "XGBoost", "lightgbm": "LightGBM", "catboost": "CatBoost",
    "huggingface": "Hugging Face", "hugging face": "Hugging Face", "hf": "Hugging Face",
    "hugging face transformers": "Hugging Face", "transformers": "Transformers",
    "langchain": "LangChain", "langgraph": "LangGraph", "llamaindex": "LlamaIndex", "llama index": "LlamaIndex",
    "onnx": "ONNX", "tensorrt": "TensorRT", "cuda": "CUDA", "opencv": "OpenCV", "spacy": "spaCy",
    "pandas": "pandas", "numpy": "NumPy", "scipy": "SciPy", "polars": "Polars", "mlflow": "MLflow",
    "kubeflow": "Kubeflow", "airflow": "Airflow", "apache airflow": "Airflow", "dbt": "dbt",
    "dagster": "Dagster", "prefect": "Prefect", "ray": "Ray", "vllm": "vLLM", "weights & biases": "Weights & Biases",
    "wandb": "Weights & Biases", "w&b": "Weights & Biases", "fastapi": "FastAPI", "flask": "Flask",
    "django": "Django", "streamlit": "Streamlit", "power bi": "Power BI", "powerbi": "Power BI",
    "tableau": "Tableau",
    # data / big data
    "spark": "Spark", "apache spark": "Spark", "pyspark": "PySpark", "sparkml": "SparkML", "kafka": "Kafka",
    "apache kafka": "Kafka", "flink": "Flink", "apache flink": "Flink", "hadoop": "Hadoop",
    "databricks": "Databricks", "snowflake": "Snowflake", "bigquery": "BigQuery", "google bigquery": "BigQuery",
    "redshift": "Redshift", "delta lake": "Delta Lake", "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "mysql": "MySQL", "mongodb": "MongoDB", "elasticsearch": "Elasticsearch", "neo4j": "Neo4j",
    "nosql": "NoSQL", "etl": "ETL", "elt": "ELT", "etl/elt": "ETL",
    # cloud / infra
    "aws": "AWS", "amazon web services": "AWS", "gcp": "GCP", "google cloud": "GCP",
    "google cloud platform": "GCP", "azure": "Azure", "microsoft azure": "Azure", "ms azure": "Azure",
    "k8s": "Kubernetes", "kubernetes": "Kubernetes", "docker": "Docker", "terraform": "Terraform",
    "ci/cd": "CI/CD", "cicd": "CI/CD", "ci cd": "CI/CD", "git": "Git", "github": "GitHub", "gitlab": "GitLab",
    "github actions": "GitHub Actions", "linux": "Linux", "sagemaker": "SageMaker", "aws sagemaker": "SageMaker",
    "vertex ai": "Vertex AI", "azure ml": "Azure ML", "azure machine learning": "Azure ML",
    "openai api": "OpenAI API", "azure openai": "Azure OpenAI", "aws bedrock": "Bedrock", "bedrock": "Bedrock",
    # concepts
    "llm": "LLMs", "llms": "LLMs", "large language models": "LLMs", "large language model": "LLMs",
    "genai": "Generative AI", "gen ai": "Generative AI", "generative ai": "Generative AI",
    "rag": "RAG", "retrieval augmented generation": "RAG", "retrieval-augmented generation": "RAG",
    "graphrag": "GraphRAG", "nlp": "NLP", "natural language processing": "NLP", "cv": "Computer Vision",
    "computer vision": "Computer Vision", "ml": "Machine Learning", "machine learning": "Machine Learning",
    "deep learning": "Deep Learning", "dl": "Deep Learning", "mlops": "MLOps", "ml ops": "MLOps",
    "llmops": "LLMOps", "reinforcement learning": "Reinforcement Learning", "rl": "Reinforcement Learning",
    "statistics": "Statistics", "statistik": "Statistics", "a/b testing": "A/B Testing", "ab testing": "A/B Testing",
    "time series": "Time Series", "time-series": "Time Series", "time series forecasting": "Time Series Forecasting",
    "prompt engineering": "Prompt Engineering", "fine-tuning": "Fine-Tuning", "fine tuning": "Fine-Tuning",
    "llm fine-tuning": "LLM Fine-Tuning", "vector databases": "Vector Databases", "vector db": "Vector Databases",
    "vector database": "Vector Databases", "agents": "AI Agents", "ai agents": "AI Agents",
    "agentic ai": "Agentic AI", "rest": "REST APIs", "rest api": "REST APIs", "rest apis": "REST APIs",
    "microservices": "Microservices", "data modeling": "Data Modeling", "data modelling": "Data Modeling",
    "argocd": "Argo CD", "argo cd": "Argo CD", "infrastructure-as-code": "Infrastructure as Code",
    "iac": "Infrastructure as Code", "ai/automation": "AI Automation", "n8n": "n8n", "dbt": "dbt",
    "pandas": "pandas", "api": "APIs", "apis": "APIs", "ms fabric": "Microsoft Fabric", "fabric": "Microsoft Fabric",
    "llm evaluation": "LLM Evals", "llm evals": "LLM Evals", "evals": "LLM Evals",
    # --- curated decisions inherited from the cloud agent's analysis_gen (Jun–Jul 2026) ---
    "langgraph": "LangGraph", "crewai": "CrewAI", "langsmith": "LangSmith", "autogen": "AutoGen",
    "ollama": "Ollama", "openai": "OpenAI", "openai api": "OpenAI", "anthropic": "Anthropic",
    "mistral": "Mistral", "llama": "Llama", "amazon sagemaker": "SageMaker", "datamesh": "Data Mesh",
    "datavault": "Data Vault", "ms-sql": "MS SQL", "restful api": "REST APIs", "restful apis": "REST APIs",
    "time-series forecasting": "Time Series Forecasting", "time-series analysis": "Time Series Forecasting",
    "time series analysis": "Time Series Forecasting",
    "recommendation systems": "Recommender Systems", "recommender systems": "Recommender Systems",
    "vision language models": "Vision-Language Models", "vlms": "Vision-Language Models",
    # NOTE (curated): "Data Warehouse" vs "Data Warehousing" stay SPLIT (artifact vs practice).
}

_SMALL = {"and", "or", "of", "for", "with", "in", "to", "as", "the", "a", "on"}

def _title(s):
    """'data pipelines' / 'Data pipelines' -> 'Data Pipelines'; keeps acronyms and mixed-case tokens."""
    words = s.split(" ")
    out = []
    for i, w in enumerate(words):
        if i == 0 or w not in _SMALL:
            w = "-".join(p[:1].upper() + p[1:] if p.islower() and p not in _SMALL else p for p in w.split("-"))
        out.append(w)
    return " ".join(out)

def canon(skill):
    s = re.sub(r"\s+", " ", (skill or "").strip().strip(".,;:")).strip()
    if not s or len(s) > 60:
        return ""
    hit = ALIASES.get(s.lower())
    if hit:
        return hit
    if " " in s or "-" in s:
        s = _title(s)
    elif s.islower() and len(s) > 3:
        s = s[:1].upper() + s[1:]
    return s

def canon_list(items):
    if isinstance(items, str):
        t = items.strip()
        if t.startswith("[") and t.endswith("]"):       # stringified Python list (seen in Jun 2026 rows)
            import ast
            try:
                v = ast.literal_eval(t)
                if isinstance(v, (list, tuple)):
                    items = [str(x) for x in v]
            except (ValueError, SyntaxError):
                pass
        if isinstance(items, str):
            items = re.split(r";", items) if ";" in items else re.split(r"[;,]", items)
    out, seen = [], set()
    items = [p for it in (items or []) for p in str(it).split(";")]   # ';' is the CSV list separator
    for it in items:
        c = canon(it)
        if c and c.lower() not in seen:
            seen.add(c.lower()); out.append(c)
    return out
