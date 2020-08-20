FROM openjdk:8-jre-slim
RUN apt-get update && apt-get install -y curl

WORKDIR /opt
RUN curl -O https://archive.apache.org/dist/lucene/solr/4.9.1/solr-4.9.1.tgz
RUN tar xzf solr-4.9.1.tgz

COPY schema.xml /opt/solr-4.9.1/example/solr/collection1/conf/

WORKDIR /opt/solr-4.9.1/example
CMD ["java", "-jar", "start.jar"]
