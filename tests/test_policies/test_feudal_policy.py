
import numpy as np
import unittest

from feudal_networks.policies.feudal_policy import FeudalPolicy
import tensorflow as tf

class TestFeudalPolicy(unittest.TestCase):

    def setUp(self):
        # reset graph before each test case
        tf.reset_default_graph()

    def test_init(self):
        global_step = tf.get_variable("global_step", [], tf.int32,\
                                        initializer=tf.constant_initializer(0, dtype=tf.int32),
                                        trainable=False)
        feudal = FeudalPolicy((80,80,3), 4, global_step)

    def test_fit_simple_dataset(self):
        with tf.Session() as session:
            global_step = tf.get_variable("global_step", [], tf.int32,\
                                            initializer=tf.constant_initializer(0, dtype=tf.int32),
                                            trainable=False)
            obs_space = (80,80,3)
            act_space = 2
            lr = 1e-4
            g_dim = 256
            worker_hid_dim = 32
            manager_hid_dim = 256
            pi = FeudalPolicy(obs_space, act_space, global_step)

            grads = tf.gradients(pi.loss, pi.var_list)

            prints = []
            for g in grads:
                prints.append(g.op.name)
                prints.append(g)
            # grads[0] = tf.Print(grads[0],prints)
            grads, _ = tf.clip_by_global_norm(grads, 40)
            grads_and_vars = list(zip(grads, pi.var_list))
            opt = tf.train.AdamOptimizer(1e-4)
            train_op = opt.apply_gradients(grads_and_vars)

            # train_op = tf.train.AdamOptimizer(lr).minimize(pi.loss,var_list=pi.var_list)
            session.run(tf.global_variables_initializer())

            obs = [np.zeros(obs_space), np.zeros(obs_space)]
            a = [[1,0], [0,1]]
            returns = [0, 1]
            s_diff = [np.ones(g_dim), np.ones(g_dim)]
            gsum = [np.zeros((1,g_dim)), np.ones((1,g_dim))]
            ri = [0, 0]

            _,features = pi.get_initial_features()
            worker_features = features[0:2]
            manager_features = features[2:]

            feed_dict = {
                pi.obs: obs,
                pi.ac: a,
                pi.r: returns,
                pi.s_diff: s_diff,
                pi.prev_g: gsum,
                pi.ri: ri,
                pi.state_in[0]: worker_features[0],
                pi.state_in[1]: worker_features[1],
                pi.state_in[2]: manager_features[0],
                pi.state_in[3]: manager_features[1]
            }

            n_updates = 10000
            for i in range(n_updates):
                loss,vf,policy, _ = session.run([pi.loss,pi.manager_vf,pi.pi, train_op], feed_dict=feed_dict)
                print(loss)
                print(policy)
                print('---------')

            # session.run(pi.pi,feed_dict)

if __name__ == '__main__':
    unittest.main()
