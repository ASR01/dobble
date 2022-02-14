# Dobble

I have done this project for the end of my training as AI Engineer at Strive School. And therefore here it is.



## Folder Structure

- docs

  Here are some images and other information used by these Readme.md

- docker_files.

  Here are the docker images for the NLP and the CV modules.

  - CV

  - NLP

    (the already built docker apps are under reeavsr/mirinda(CV) and reeavsr/sinalco(NLP) to be found in docker hub)

- ST_App

  Streamlit application.

- Data

  The images needed to run the application. (it would have been nice to do it with live imaging but my computer has its limitations).

## How to install it and run it

### Download it 



### NLP in Docker

Open your terminal and supposing you have your docker installed build it, go to the folder where the  

`docker build -t nlp .`

And to run it do it with:

`docker run --rm -it -p 8001:8000 nlp`

### CV in Docker

Open your terminal and supposing you have your docker installed build it, go to the folder where the  

`docker build -t cv .`

And to run it do it with:

`docker run --rm -it -p 8002:8000 cv`

With both docker up and running we can run our app locally 

1. Make an **virtualenv** with the name you like.

2. Install the modules needed in *requiments.txt*

   `pip install -r requirements.txt`

3. Activate the environment.

4. Run the **streamlit** app. 

   `streamlit run app.py` (if you are not in the *ST_app* folder you will have to give the path)

   