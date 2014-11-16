import click


@click.group()
@click.option('-t', '--threads', default=1, help='Number of threads to use \
(only affects modules that are designed to do parallel processing)')
@click.pass_context
def cli(ctx, threads):
    ctx.obj['MSNOISE_threads'] = threads
    pass


@click.command()
def install():
    """This command launches the installer."""
    click.echo('Launching the installer')
    from ..s000installer import main
    main()


@click.command()
def config():
    """This command launches the Configurator."""
    click.echo('Let\'s Configure MSNoise !')
    from ..s001configurator import main
    main()
    

@click.command()
@click.option('-s', '--sys', is_flag=True, help='System Info')
@click.option('-m', '--modules', is_flag=True, help='Modules Info')
@click.option('-e', '--env', is_flag=True, help='Environment Info')
@click.option('-a', '--all', is_flag=True, help='All Info')
@click.pass_context
def bugreport(ctx, sys, modules, env, all):
    """This command launches the Bug Report script."""
    click.echo('Let\'s Bug Report MSNoise !')
    click.echo('Working on %i threads' % ctx.obj['MSNOISE_threads'])
    from ..bugreport import main
    main(sys, modules, env, all)

@click.command()
def populate():
    """Rapidly scan the archive filenames and find Network/Stations"""
    from ..s002populate_station_table import main
    main()

@click.command()
@click.option('-i', '--init', is_flag=True, help='First run ?')
@click.pass_context
def scan_archive(ctx, init):
    """Scan the archive and insert into the Data Availability table."""
    from ..s01scan_archive import main
    main(init, ctx.obj['MSNOISE_threads'])


@click.command()
def new_jobs():
    """Determines if new CC jobs are to be defined"""
    from ..s02new_jobs import main
    main()


@click.command()
def compute_cc():
    """Computes the CC jobs (based on the "New Jobs" identified)"""
    from ..s03compute_cc import main
    main()


@click.command()
@click.option('-r', '--ref', is_flag=True, help='Compute the REF Stack')
@click.option('-m', '--mov', is_flag=True, help='Compute the MOV Stacks')
@click.option('-i', '--interval', default=1, help='Number of days before now to\
 search for modified Jobs')
def stack(ref, mov, interval):
    """Stacks the [REF] and/or [MOV] windows"""
    click.secho('Lets STACK !', fg='green')
    from ..s04stack import main
    if ref:
        main('ref', interval)
    if mov:
        main('mov', interval)


@click.command()
def compute_mwcs():
    """Computes the MWCS based on the new stacked data"""
    from ..s05compute_mwcs import main
    main()


@click.command()
def compute_dtt():
    """Computes the dt/t jobs based on the new MWCS data"""
    from ..s06compute_dtt import main
    main()


@click.command()
@click.argument('jobtype')
def reset(jobtype):
    """Resets the job to "T"odo. ARG is [CC] or [DTT]"""
    from ..msnoise_table_def import Job
    from ..database_tools import connect
    
    session = connect()
    jobs = session.query(Job).filter(Job.type == jobtype).all()
    for job in jobs:
        job.flag = 'T'
    session.commit()
    session.close()

###
### PLOT GROUP
###

@click.group()
def plot():
    """Top level command to trigger different plots"""
    pass


@click.command()
def data_availability():
    """Plots the Data Availability vs time"""
    from ..plots.data_availability import main
    main()


@click.command()
@click.option('-a', '--all', default=True, help='Plot All mov stacks')
@click.option('-m', '--mov_stack', default=0,  help='Plot specific mov stacks')
@click.option('-s', '--savefig', is_flag=True, help='Save figure to disk (PNG)')
def dvv(all, mov_stack, savefig):
    """Plots the dv/v (parses the dt/t results)"""
    from ..plots.dvv import main
    main(all, mov_stack, savefig)


@click.command()
@click.option('--sta1', help='Plot All mov stacks')
@click.option('--sta2',  help='Plot specific mov stacks')
@click.option('-f', '--filterid', default=1, help='Save figure to disk (PNG)')
@click.option('-c', '--comp', default="ZZ", help='Save figure to disk (PNG)')
def interferogram(sta1, sta2, filterid, comp):
    """Plots the dv/v (parses the dt/t results)"""
    from ..plots.interferogram import main
    main(sta1, sta2, filterid, comp)


# Add plot commands to the plot group:
plot.add_command(data_availability)
plot.add_command(dvv)
plot.add_command(interferogram)


# Add all commands to the cli group:
cli.add_command(install)
cli.add_command(config)
cli.add_command(populate)
cli.add_command(bugreport)
cli.add_command(scan_archive)
cli.add_command(new_jobs)
cli.add_command(compute_cc)
cli.add_command(stack)
cli.add_command(compute_mwcs)
cli.add_command(compute_dtt)
cli.add_command(reset)

# Finally add the plot group too:
cli.add_command(plot)


def run():
    cli(obj={})