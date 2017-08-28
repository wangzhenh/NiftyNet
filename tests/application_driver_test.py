import numpy as np
import tensorflow as tf
from niftynet.engine.application_driver import ApplicationDriver
from niftynet.io.misc_io import set_logger


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def get_initialised_driver():
    system_param = {
        'SYSTEM': Namespace(
            action='train',
            num_threads=4,
            num_gpus=4,
            cuda_devices='',
            model_dir='./testing_data'),
        'NETWORK': Namespace(
            batch_size=50,
            name='tests.toy_application.TinyNet'),
        'TRAINING': Namespace(
            starting_iter=0,
            max_iter=500,
            save_every_n=0,
            tensorboard_every_n=1,
            max_checkpoints=20,
            optimiser='niftynet.engine.application_optimiser.Adagrad',
            lr=0.01),
        'CUSTOM': Namespace(
            vector_size=100,
            mean=10.0,
            stddev=2.0,
            name='tests.toy_application.ToyApplication')
    }
    app_driver = ApplicationDriver()
    app_driver.initialise_application(system_param, {})
    return app_driver


class ApplicationDriverTest(tf.test.TestCase):
    def test_app_stop(self):
        test_driver = get_initialised_driver()
        test_driver.graph = test_driver._create_graph()
        with self.test_session(graph=test_driver.graph) as sess:
            sess.run(test_driver._init_op)
            coord = tf.train.Coordinator()
            for sampler in test_driver.app.get_sampler():
                sampler.run_threads(sess, coord, test_driver.num_threads)
            i, train_op = test_driver.app.training_ops(0, 5).next()
            test_driver.app.stop()
            try:
                while True:
                    sess.run(train_op)
            except tf.errors.OutOfRangeError:
                for thread in test_driver.app.sampler[0]._threads:
                    self.assertFalse(thread.isAlive(), "threads not closed")

    def test_training_update(self):
        test_driver = get_initialised_driver()
        test_driver.graph = test_driver._create_graph()
        with self.test_session(graph=test_driver.graph) as sess:
            sess.run(test_driver._init_op)
            coord = tf.train.Coordinator()
            for sampler in test_driver.app.get_sampler():
                sampler.run_threads(sess, coord, test_driver.num_threads)
            i, train_op = test_driver.app.training_ops(0, 5).next()
            var_0 = sess.run(tf.global_variables()[0])
            sess.run(train_op)
            var_1 = sess.run(tf.global_variables()[0])
            square_diff = np.sum(var_0 - var_1)**2
            self.assertGreater(square_diff, 0.0)
            test_driver.app.stop()

    def test_multi_device_inputs(self):
        test_driver = get_initialised_driver()
        test_driver.graph = test_driver._create_graph()
        with self.test_session(graph=test_driver.graph) as sess:
            sess.run(test_driver._init_op)
            import pdb; pdb.set_trace()
            coord = tf.train.Coordinator()

if __name__ == "__main__":
    set_logger()
    tf.test.main()