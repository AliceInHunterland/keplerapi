FROM continuumio/miniconda3
ADD . /keplerApi
WORKDIR /keplerApi


RUN conda install geojson shapely geopandas -c conda-forge

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

# Demonstrate the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# The code to run when container is started:
COPY main.py .
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "myenv", "python", "main.py"]
RUN pip install -r requirements.txt