from _common import arguments, emit
from pipeline import run

args=arguments("Run the aggregate-only public reproducibility pipeline")
emit(run(args.config))

