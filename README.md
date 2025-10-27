# Badass simple containers demo

step 1. install podman

step 2. create a linux machine

	podman machine init --cpus 8 --memory 8192 --user-mode-networking --rootful

step 3. To build your image: 

	podman build -t my-python-app .

step 4. To run your container: 

	podman run -it -p 9000:8000 my-python-app

step 5. Test your application from a different shell:

	curl http://localhost:9000/hello/victor
