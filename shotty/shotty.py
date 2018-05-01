import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
        instances = []

        if project:
            filters = [{'Name':'tag:Project', 'Values':[project]}]
            instances = ec2.instances.filter(Filters=filters)
        else:
            instances = ec2.instances.all()

        return instances

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>'))))

    return

@instances.command('stop')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--force', 'use_force', default=None, is_flag=True,
    help="You have to use --force flag to stop instances")
def stop_instances(project, use_force):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        if project or use_force:
            print('Stopping {0}...'.format(i.id))
            try:
                i.stop()
            except botocore.exceptions.ClientError as e:
                print(" Could not stop {0}.".format(i.id) + str(e))
                continue
        else:
            print("You have to specify the project or use the --force flag to stop instances")
            break

    return

@instances.command('start')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--force', 'use_force', default=None, is_flag=True,
    help="You have to use --force flag to start instances")
def start_instances(project, use_force):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        if project or use_force:
            print('Starting {0}...'.format(i.id))
            try:
                i.start()
            except botocore.exceptions.ClientError as e:
                print(" Could not start {0}.".format(i.id) + str(e))
                continue
        else:
            print("You have to specify the project or use the --force flag to start instances")
            break

    return

@instances.command('reboot')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
@click.option('--force', 'use_force', default=None, is_flag=True,
    help="You have to use --force flag to reboot instances")
def reboot_instances(project, use_force):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        if project or use_force:
            print('Starting {0}...'.format(i.id))
            try:
                i.reboot()
            except botocore.exceptions.ClientError as e:
                print(" Could not reboot {0}.".format(i.id) + str(e))
                continue
        else:
            print("You have to specify the project or use the --force flag to reboot instances")
            break

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")

def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(', '.join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
                )))

    return

@volumes.command('snapshot',
    help="Create snapshots of all volumes")
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--force', 'use_force', default=None, is_flag=True,
    help="You have to use --force flag to snapshot volumes")
def create_snapshots(project, use_force):
    "Create snapshots for EC2 volumes"

    instances = filter_instances(project)
    for i in instances:
        if project or use_force:
            print("Stopping {0}...".format(i.id))

            i.stop()
            i.wait_until_stopped()

            for v in i.volumes.all():
                if has_pending_snapshot(v):
                    print("   Skipping {0}, snapshot already in progress".format(v.id))
                    continue
                print("   Creating snapshot of {0}".format(v.id))
                v.create_snapshot(Description="Created by snappy")

            print("Starting {0}...".format(i.id))

            i.start()
            i.wait_until_running()
        else:
            print("You have to specify the project or use the --force flag to snapshot volumes")
            break

    return


@cli.group()
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each voluem, not just the most recent")
def list_snapshots(project, list_all):
    "List EC2 snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

                if s.state == "completed" and not list_all:
                    break
    return






if __name__ == '__main__':
    cli()
