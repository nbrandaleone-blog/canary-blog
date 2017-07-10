# Canary Blue/Green deployments on ECS

This reference architecture is a companion to the blog post on 
[canary blue green deployments on ECS](https://aws.amazon.com/blogs/compute/ecs.../). 
In order to provide an automated and safe method of migrating traffic from a blue deployment
to a green one, it leverages Route53 weights to adjust the traffic flow from one service to another.
It associates a new service with a separate Application Load Balancer, leveraging ECS Event Streams 
to trigger the deployment. Once triggered, Step Functions handle the transitioning of traffic 
off of the blue ALB to the green one. If the Step Function detects a failure of the green service,
it will automatically fail-back to the original configuration. The one concern users may have
is that DNS propogation delay of approximately 60 seconds will be introduced between migration
increments.

## Pre-Requisites
This example uses [AWS Command Line Interface](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) to run Step-3 below.

Pease follow [instructions](http://docs.aws.amazon.com/cli/latest/userguide/installing.html) if you haven't installed AWS CLI. Your CLI [configuration](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) need PowerUserAccess and IAMFullAccess [IAM policies](http://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html) associated with your credentials

```console
aws --version
```

Output from above must yield **AWS CLI version >= 1.11.37** 

## From here down rewrite!
## Quick setup in three steps

#### 1. Fork ECS Sample app

[Fork](https://help.github.com/articles/fork-a-repo/) the [Amazon ECS sample app](https://github.com/awslabs/ecs-demo-php-simple-app) GitHub repository into your GitHub account.

Clone the ECS Sample app repo 
```console
git clone https://github.com/<your_github_username>/ecs-demo-php-simple-app
```

#### 2. Clone ECS blue green repo

```console
git clone https://github.com/awslabs/ecs-blue-green-deployment
```

#### 3. Run bin/deploy
```console
bin/deploy
```

Here are the inputs required to launch CloudFormation templates:
  * **S3 Bucket**: Enter S3 Bucket for storing your CloudFormation templates and scripts. This bucket must be in the same region where you wish to launch all the AWS resources created by this example.
    * **CloudFormation Stack Name**: Enter CloudFormation Stack Name to create stacks
      * **GitHubUser**: Enter your GitHub Username
        * **GitHubToken**: Enter your GitHub Token for authentication ([https://github.com/settings/tokens](https://github.com/settings/tokens))

        Sit back and relax until all the resources are created for you. After the templates are created, you can open ELB DNS URL to see the ECS Sample App

        For testing Blue Green deployment, Go ahead and make a change in ECS Sample App. For ex, edit src/index.php and update the background-color to #20E941 to change to Green background color. After commiting to your repo, Code Pipeline will pick the change automatically and go through the process of updating your application. 

        Click on "Review" button in Code pipeline management console and Approve the change. Now you should see the new version of the application with Green background. 

        ## Resources created in this exercise

        Count | AWS resources 
        | --- | --- |
        7   | [AWS CloudFormation templates](https://aws.amazon.com/cloudformation/)
        1   | [Amazon VPC](https://aws.amazon.com/vpc/) (10.215.0.0/16)   
        1  | [AWS CodePipeline](https://aws.amazon.com/codepipeline/) 
        2  | [AWS CodeBuild projects](https://aws.amazon.com/codebuild/) 
        1  | [Amazon S3 Bucket](https://aws.amazon.com/s3/) 
        1  | [AWS Lambda](https://aws.amazon.com/lambda/) 
        1  | [Amazon ECS Cluster](https://aws.amazon.com/ecs/) 
        2  | [Amazon ECS Service](https://aws.amazon.com/ecs/) 
        1  | [Application Load Balancer](https://aws.amazon.com/elasticloadbalancing/applicationloadbalancer/) 
        2  | [Application Load Balancer Target Groups](https://aws.amazon.com/elasticloadbalancing/applicationloadbalancer/) 


        ## Implementation details
        During first phase, the parent template (ecs-blue-green-deployment.yaml) kicks off creating VPC and the resources in deployment-pipeline template. This creates CodePipeline, CodeBuild and Lambda resources. Once this is complete, second phase creates the rest of resources such as ALB, Target Groups and ECS resources. Below is a screenshot of CodePipeline once all CloudFormation templates are completed


        ![codepipeline](images/codepipeline.png)



        The templates create two services on ECS cluster and associates a Target Group to each service as depicted in the diagram. Blue Target Group is associated with Port 80 that represents Live/Production traffic and Green Target Group is associated with Port 8080 and is available for new version of the Application. During initial rollout, both Blue and Green service serve same application versions. As you introduce new release, CodePipeline picks those changes and are pushed down the pipeline using CodeBuild and deployed to the Green service. In order to switch from Green to Blue service (or from beta to Prod environment), you have to **Approve** the release by going to CodePipeline management console and clicking **Review** button. Approving the change will trigger Lambda function (blue_green_flip.py) which does the swap of ALB Target Groups. If you discover bugs while in Production, you can revert to previous application version by clicking and approving the change again. This in turn will put Blue service back into Production. To simplify identifying which Target Groups are serving Live traffic, we have added Tags on ALB Target Groups. Target Group **IsProduction** Tag will say **true** for Production application. 


        ![bluegreen](images/ecs-bluegreen.png)



        Here is further explaination for each stages of Code Pipeline.  

        <u>**Build stage**</u>

        * During first phase of build stage, CodeBuild builds the docker container image and pushes to [Amazon ECR](https://aws.amazon.com/ecr/).
         
         * During second phase, Codebuild executes scripts/deployer.py which executes the following scripted logic

           1. Retrieve artifact (build.json) from the previous phase (CodeBuild phase, which builds application container images)
             2. Check if the load balancer exists. Name of the ELB is fed through environment variable by the pipeline.
               3. Get tag key value of the target group, running on port 8080 and 80 with KeyName as "Identifier". It will be either "Code1" or "Code2"
                 4. Get Sha of the image id running on target group at port 8080 and 80
                   5. Edit the build.json retrieved from step-1 and append the values retrieved in step3 and step4
                     6. Save the modified build.json. This file is the output from codebuild project and fed as an input to the CloudFormation
                          execution stage.This json file has the following schema
                                {
                                        "Code1" : "CONTAINER_TAG1",
                                                "Code2" : "CONTAINER_TAG2"
                                                      }
                                                        If the load balancer does not exists (as found in step-2), this would imply that the stack is executed for the first time, and the values of "CONTAINER_TAG1" and CONTAINER_TAG2" will be the same and default to the
                                                          value retrieved from build.json in step-1

                                                          <u>**Deploy stage**</u>
                                                          CodePipeline executes templates/ecs-cluster.yaml. The CloudFormation input parameters with KeyName as "Code1" and "Code2" are overwritten with the values as written in the build.json, retrieved from the second phase of Build Stage.

                                                          <u>**Review stage**</u>
                                                          The pipeline offers manual "Review" button so that the approver can review code and Approve new release.
                                                          Providing approvals at this stage will trigger the Lambda function (blue_green_flip.py) which swaps the Green Target Group to Live traffic. You can checkout sample app to see new release change. blue_green_flip.py has the following logic scripted

                                                             1. Read Job Data from input json
                                                                2. Read Job ID from input json
                                                                   3. Get parameters from input json
                                                                      4. Get Load balancer name from parameters
                                                                         5. Identify the TargetGroup running on this Load Balancer at port 80 and port 8080. Perform the TargetGroup Swap. Also swap the values of "IsProduction" tags.
                                                                            6. Send success or failure to CodePipeline

                                                                            ## Cleanup
                                                                            First delete ecs-cluster CloudFormation stack, this will delete both ECS services (BlueService and GreenService) and LoadBalancer stacks. Next delete the parent stack. This should delete all the resources that were created for this exercise 
