# Collect Logs for the CloudPassage Halo App

The CloudPassage Halo App uses the Halo REST API and AWS Lambda to collect Halo events.  

To collect CloudPassage Halo logs for Sumo Logic you need to configure:

1. Two Sumo Logic hosted collectors.
2. Two Lambda functions to call Halo’s REST APIs and forward Halo events to Sumo Logic.
![ScreenShot](https://help.sumologic.com/@api/deki/files/3452/CloudPassage2.png?revision=3)

## Sumo Logic Collector Configuration
If this is the first time you are creating an HTTPS collector, review how to create an HTTP source. Then, follow the instructions on how to [create a collector](https://help.sumologic.com/07Sumo-Logic-Apps/22Security_and_Threat_Detection/CloudPassage_Halo/01Collect-Logs-for-the-CloudPassage-Halo-App#Create_the_collector).

#### Create the collector
1. Click Manage Data > Collection > Add Collector.
2. Click Hosted Collector.
3. In Add Hosted Collector enter:
    Name. Halo_Lambda_Ingestor.
    Description. Halo Events Collector.
    Category. CP_Halo.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3456/image9.png?revision=1&size=bestfit&width=527&height=319)
    And click Save.
4. Click OK to add a source to your collector.
5. Select HTTP as the source type.
6. Enter the information as below for Halo Security Events.
    <b>Name</b>. CP_Halo_Workload_Security_Events_Collector.
    <b>Description</b>. Halo Security Events Collector.
    <b>Source Host</b>. CP_Halo.
    <b>Source Category</b>. halo/workload/security/events
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3457/image11.png?revision=1)
7. Click <b>Save</b>. Be sure to note the endpoint URL provided for this collection. You will need it later.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3460/image3.png?revision=1&size=bestfit&width=566&height=284)
8. Create a second source.
9. Click Hosted Collector.
10. Select HTTP as the source type.
11. Enter the information as below for Halo Metric Events.
    <b>Name</b>. CP_Halo_Metrics_Collector.
    <b>Description</b>. Halo key metrics collector.
    <b>Source Host</b>. CP_Halo.
    <b>Source Category</b>. halo/metrics.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3463/image15.png?revision=1)
12. When you are done, you should have two collections `CP_Halo_Metrics_Collector` and  `CP_Halo_Workload_Security_Events_Collector` set up under a single collector `Halo_Lambda_Ingestor`.


## CloudPassage Halo
To set up CloudPassage Halo, do the following:

1. Use the official [CloudPassage documentation](https://www.cloudpassage.com/) to set up CloudPassage. You will need your CloudPassage login. 
2. Follow the instructions on how to create a [read-only API key](https://library.cloudpassage.com/help/working-with-groups#api-keys) for the App.


## AWS Configuration
<b>SQS (Simple Queue Service)</b>: This queue stores one message at any given time.  It contains “the last time (in Zulu format)” the script ran to collect the events from Halo.  The message is then deleted and new one (with the current time in Zulu format) is added into the queue.

The queue is automatically created the first time you run the `Halo_events_to_SumoLogic` Lambda code.

#### Lambda Functions
If this is the first time you are using the Lambda, it is strongly recommended to go through [Quick start with Lambda](http://docs.aws.amazon.com/lambda/latest/dg/getting-started.html) first.

#### Recommended configuration

Download the Python code from the following two zip file links:

1. [Halo_events_to_SumoLogic.zip](https://github.com/cloudpassage/halo-sumologic/raw/master/Halo_events_to_SumoLogic.zip) - Python Lambda code to collect Halo events and forward them to Sumo Logic. This Python Lambda code would use Halo’s API to collect the security events reported by the agents installed in your workloads.  It takes the “last time” the Lambda code ran from the SQS.  Then initiate API call(s) to request any events that has been reported between the “last time” the Lambda code ran and the current time. It uses the SQS to store the “last time” the event was collected.

2. [Halo_metrics_to_SumoLogic.zip](https://github.com/cloudpassage/halo-sumologic/raw/master/Halo_metrics_to_SumoLogic.zip) - Python Lambda code to collect Halo metrics and forward them to Sumo Logic. This Python Lambda code would use Halo’s API to collect the key stats from your Halo account.   

#### Configure AWS Lambda for Halo_events_to_SumoLogic
Sample policy: Be sure to use the proper permission level.
1. Configure Lambda.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3464/image22.png?revision=1)
2. Click <b>Blank Function</b>.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3482/image31.png?revision=1)
3. Click Next.
4. Fill in Configure Function with:
    <b>Name</b>. halo_events_to_sumologic.
    <b>Runtime</b>. Python 2.7.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3465/image33.png?revision=1)
5. Change `Code entry Type` to `Upload a .ZIP` file.  And upload the `Halo_events_to_SumoLogic.zip` file.  Then enter in the environment variables with proper values (refer to the steps above).
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3469/image14.png?revision=1)
6. Fill in the information to match the screenshot below.  Enter `halo_events_to_sumologic.lambda_handler` for `Handler`.  Then select “Create a custom role” for `Role`.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3483/image27.png?revision=1)
7. Fill in the information to match the screenshot below.  Select “Choose a new IAM Role” for IAM Role and `lambda_basic_execution` for `Role Name`.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3485/image4.png?revision=1)
8. Change the `Timeout` to `4 minutes` under `Advanced Settings`.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3487/image19.png?revision=1)
9. Verify all the information is entered correctly. Then click <b>Create Function</b> to proceed.
10. Now we need to create an IAM role. Select <b>IAM</b>.
11. Select <b>lamda_basic_execution</b> role that was created in the previous step.
12. Select <b>AmazonSQSFullAccess</b> and <b>AWSLambdaBasicExecutionRole</b> for the policies. If you don’t have these policies, refer to the AWS manual and next few steps to create them.
13. Here is the sample policy for the <b>AmazonSQSFullAccess</b>.  Make sure you change the permission to meet your security requirements.
14. Here is the sample policy for <b>AWSLambdaBasicExecutionRole</b>. Make sure you change the permission to meet your security requirements.
15. Let’s test the Lambda code.  Click on `Test` and then `Save` and test to start the code.
16. If it is configured properly, it should create the SQS queue for you.  And the outcome should look something similar to below.  Result should show you the time in Zulu format and Log Output should include create_queue.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3480/image34.png?revision=1)
17. If you check the SQS dashboard, you will see the new queue, `last_time_scan`, has been created for you automatically.
18. Let's create a trigger for our Lambda code.  I want this code to run every 5 minutes. Select Triggers from the tab.  Then click <b>Add trigger</b>.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3484/image5.png?revision=1)
19. Then click on the blank square to bring out the pulldown menu.  Select <b>CloudWatch Events - Schedule</b>.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3481/image32.png?revision=1)
20. Fill in the information and make sure you set the <b>Schedule expression</b> as <b>rate(5 minutes)</b>.
21. A successfully configured trigger will have a success message and appear similar to the trigger below.
    ![ScreenShot](https://help.sumologic.com/@api/deki/files/3488/image21.png?revision=1)
22.  You are done for the first Lambda code!  You can follow the same steps to configure <b>Lambda for Halo_metrics_to_SumoLogic</b>.


## Building zip archives from source:
1. Clone this repo locally and descend into the root directory of the repo.
2. Build the container image: `docker build -t halo-sumologic:latest` .
3. Export the lambda archives: `docker run -it --rm -v /tmp/halo-sumologic:/var/export halo-sumologic:latest cp -r /var/output/ /var/export/`