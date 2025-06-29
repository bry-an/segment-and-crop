# ----- Base image with LandingAI runtime & OpenVINO
FROM public.ecr.aws/landing-ai/deploy:latest

# ----- ARG lets us swap which model ZIP gets baked in
ARG MODEL_ZIP=segment.zip

# Copy the ZIP into /models inside the image
COPY models/${MODEL_ZIP} /models/model.zip

# LandingAI listens on 8001 in the container
EXPOSE 8001

# Launch the model as soon as the container starts
CMD ["run-local-model", "--model", "/models/model.zip"]