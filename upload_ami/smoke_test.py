import boto3
import time

def smoke_test(image_id, region):
    ec2 = boto3.client("ec2", region_name=region)

    # TODO per architecture
    logging.info("Starting instance")
    run_instances = ec2.run_instances(ImageId=image_id, InstanceType="t3a.nano", MinCount=1, MaxCount=1, ClientToken=image_id)

    instance_id = run_instances["Instances"][0]["InstanceId"]

    # This basically waits for DHCP to have finished; as it uses ARP to check if the instance is healthy
    logging.info(f"Waiting for instance {instance_id} to be running")
    ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])


    tries = 5
    console_output = ec2.get_console_output(InstanceId=instance_id, Latest=True)
    output = console_output.get("Output")
    while output is None:
        time.sleep(10)
        logging.info(f"Waiting for console output to become available ({tries} tries left)")
        console_output = ec2.get_console_output(InstanceId=instance_id, Latest=True)
        output = console_output.get("Output")
    print(output)


    logging.info(f"Terminating instance {instance_id}")
    ec2.terminate_instances(InstanceIds=[instance_id])
    ec2.get_waiter("instance_terminated").wait(InstanceIds=[instance_id])


if __name__ == "__main__":
    import argparse
    import logging
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--image-id", required=True)
    parser.add_argument("--region", required=True)
    args = parser.parse_args()

    smoke_test(args.image_id, args.region)