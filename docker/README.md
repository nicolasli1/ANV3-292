instrucciones 

ir a la carpeta de docker /ANV3-292/docker

ejecutar la instruccion docker build . -t image292 

ejecutar la imagen en un contenedor docker run -p 3000:3000 image292 

docker ps 

deben copiar en CONTAINER ID 

docker exec -it CONTAINER ID bash 
