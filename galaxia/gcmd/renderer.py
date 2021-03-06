# Copyright 2016 - Wipro Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and

"""
Module to start galaxia renderer service
"""
import logging
import os
import sys

from oslo_config import cfg

from galaxia.common import service
from galaxia.common.rpc import broker
from galaxia.grenderer.controller import controller

# Register options for the dashboard renderer service
API_SERVICE_OPTS = [
    cfg.StrOpt('rabbitmq_host',
               default='localhost',
               help='The host for the rabbitmq server'),
    cfg.IntOpt('rabbitmq_port',
               default='5672',
               help='The  port for the rabbitmq server'),
    cfg.StrOpt('topic',
               default='test',
               help='The topic'),
    cfg.StrOpt('rabbitmq_username',
               default='guest',
               help='The username for the rabbitmq server'),
    cfg.StrOpt('handler',
               default='prometheus',
               help='The username for the rabbitmq server')
]

log = logging.getLogger(__name__)


def main():
    service.prepare_service("grenderer", sys.argv)

    CONF = cfg.CONF
    opt_group = cfg.OptGroup(name='grenderer', title='Options for the\
                                                     renderer service')
    CONF.register_group(opt_group)
    CONF.register_opts(API_SERVICE_OPTS, opt_group)
    CONF.set_override('topic', CONF.grenderer.topic, opt_group)
    CONF.set_override('rabbitmq_host', CONF.grenderer.rabbitmq_host, opt_group)
    CONF.set_override('rabbitmq_port', CONF.grenderer.rabbitmq_port, opt_group)
    CONF.set_override('rabbitmq_username', CONF.grenderer.rabbitmq_username,
                      opt_group)
    CONF.set_override('handler', CONF.grenderer.handler, opt_group)

    handlers = {
        'prometheus': controller.Controller,
    }

    endpoints = [
        handlers[CONF.grenderer.handler](),
    ]

    log.info('Starting renderer service in PID %s' % os.getpid())

    rpc_server = broker.Broker(CONF.grenderer.topic,
                               CONF.grenderer.rabbitmq_host,
                               endpoints)
    print 'Galaxia Renderer service started in PID %s' % os.getpid()

    rpc_server.serve()
