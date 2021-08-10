# Prep for getting CNR ready to role

1) install the rolebindings in manifest 1 (don't forget to focus to your target namespace)
    *kubectl apply -f 1-event-roles.yaml*

2) Install the RabbitMQ Operator
    *kubectl apply -f https://github.com/rabbitmq/cluster-operator/releases/download/v1.6.0/cluster-operator.yml*

3) install cert-manager if not already installed    
    *kubectl create namespace cert-manager*
    *kubectl apply -f https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.yaml*

4) apply rolebinding for cert-manager in manifest 2
    *kubectl apply -f 2-event-role-cert-manager.yaml*

5) deploy the RabbitMQ topology manager with xcert-manager support
    *kubectl apply -f  apply -f https://github.com/rabbitmq/messaging-topology-operator/releases/download/v0.8.0/messaging-topology-operator-with-certmanager.yaml*

6) deploy a RabbitMQ cluster instance
    *kubectl apply -f 3-event-rabbitmq-cluster.yaml*

7) deploy the knative RabbitMQ broker in manifest 3. By using RabbitMq instead of memory based it is more resilient. change namespace as required
    *kubectl apply -f 4-event-rabbitmq-broker.yaml -n default*


