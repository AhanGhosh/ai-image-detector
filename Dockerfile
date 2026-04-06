# 1. Use a standard Python image
FROM python:3.10-slim

# 2. Set up a non-root user (Hugging Face requirement for security)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 3. Set the working directory
WORKDIR $HOME/app

# 4. Copy and install requirements first (to make builds faster)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your files (main.py and .pth models)
COPY --chown=user . .

# 6. Expose the port Hugging Face expects
EXPOSE 7860

# 7. Start the FastAPI server
# We use 'main:app' because your file is named main.py and your variable is app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]