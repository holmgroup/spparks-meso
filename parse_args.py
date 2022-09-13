import argparse


def parse_inputs():
    # see argparse help entries for each argument below
    default_n_init=2
    default_n_grow=3
    default_temperature=0.9
    default_size=256
    default_n_iter=2000000
    default_red_frac=0.2
    default_start_id=1
    default_log_iter=2000

    parser = argparse.ArgumentParser(description="Parse command line inputs for running candidate grain Monte Carlo simulations of abnormal grain growth. Outputs of simulations are stored in /home/meso/finished.")

    parser.add_argument('--n-init', dest='n_init', action='store', default=default_n_init,
            help='Number of initial microstructures to generate, default={}.'.format(default_n_init))

    parser.add_argument('--n-grow', dest='n_grow', action='store', default=default_n_grow,
            help='Number of repeated growth simulations for each initial state, default={}.'.format(default_n_grow))

    parser.add_argument('--animate', dest='animate', action='store_true',
            help='Generate animation of each grain growth simulation and store as .mov file. Not enabled by default.')

    parser.add_argument('-T', dest='T', action='store', default=default_temperature, 
            help='Monte Carlo Temperature for grain growth simulations, default={}.'.format(default_temperature))

    parser.add_argument('--size', dest='size', action='store', default=default_size,
            help='Length (number of sites) of the square 2d simulation grid, default={}.'.format(default_size))

    parser.add_argument('--n-iter', dest='n_iter', action='store', default=default_n_iter, help='Number of iterations to run grain growth simulation. Default={}'.format(default_n_iter))

    parser.add_argument('--red-frac', dest='red_frac', action='store', default=default_red_frac,help='Fraction of red grains that form high-mobility interfaces with the candidate grain in each simulation, default={}'.format(default_red_frac))

    parser.add_argument('--log-iter', dest='log_iter', action='store', default=default_log_iter, help='Number of iterations between grain size measurements, default={}'.format(default_log_iter))

    parser.add_argument('--start-id', dest='start_id', action='store', default=default_start_id, help='Starting numeric job id to use when saving results. Job ID will be incremented for each new initial state, default={}'.format(default_start_id))


    args = parser.parse_args()

    return args

def update_templates(args):

    template_dir = '/home/meso-home/candidate-grains-master-template'

    # update init template to include correct system size
    with open('{}/init_template_unformat.spkin'
            .format(template_dir), 'r') as f:
        data = f.read()
    
    with open('{}/init_template.spkin'
            .format(template_dir), 'w') as f:
        f.write(data.format(args.size, ))
    
    # update grow template to include correct temperature,
    # iterations between measurements, and total iterationts simulation is run

    with open('{}/agg_model_template_unformat.spkin'
            .format(template_dir), 'r') as f:
        data = f.read()

    with open('{}/agg_model_template.spkin'
            .format(template_dir), 'w') as f:
        f.write(data.format(args.T, args.log_iter, args.n_iter))

    return

    
def main():
    args = parse_inputs()
    update_templates(args)
    print(f'{args.n_init} {args.n_grow} {args.red_frac} {args.start_id} {int(args.animate)}')

if __name__ == "__main__":
    main()
