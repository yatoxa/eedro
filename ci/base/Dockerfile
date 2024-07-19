ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}

ARG PROJECT_HOME=/app
ARG PROJECT_SRC=${PROJECT_HOME}/src
ARG PROJECT_WD=${PROJECT_HOME}/run
ARG VENV_HOME=${PROJECT_HOME}/venv
ARG PYTHON_VENV=${VENV_HOME}/bin/python

COPY . ${PROJECT_SRC}

RUN python -m venv --copies --clear --upgrade-deps ${VENV_HOME} \
    && ${PYTHON_VENV} -m pip install -U pip

RUN ${PYTHON_VENV} -m pip install -U -r ${PROJECT_SRC}/etc/requirements.txt

RUN ${PYTHON_VENV} -m pip install -U -e ${PROJECT_SRC}

RUN echo ". ${VENV_HOME}/bin/activate" >> ~/.bashrc \
    && mkdir -p ${PROJECT_WD}

WORKDIR ${PROJECT_WD}
