# Copyright (C) 2015 Xomad. All rights reserved.
#
# This software is the confidential and proprietary information of
# Xomad or one of its subsidiaries. You shall not disclose this
# confidential information and shall use it only in accordance with
# the terms of the license agreement or other applicable agreement you
# entered into with Xomad.
#
# Xomad MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE
# SUITABILITY OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT. Xomad
# SHALL NOT BE LIABLE FOR ANY LOSSES OR DAMAGES SUFFERED BY LICENSEE
# AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
# DERIVATIVES.
#
# Created on 31/10/2015
#

from xde.helpers.singleton import SingletonMixin
from xde.services import BaseService


class ServiceRegistryException(ValueError):
    pass


class ServiceRegistry(SingletonMixin):
    __registry = dict()

    def get(self, service):
        """returns a service instance

        Args:
            service: service class

        Returns: service instance

        """
        self._ensure_valid_service(service)
        _service = self.__registry.get(service.__name__)
        if not _service:
            _service = self.register(service)
        return _service

    def register(self, service=None):
        """creates an instance of the service, initializes and then registers it into the registry

        Args:
            service: service class

        Returns: service instance created and initialized

        """
        self._ensure_valid_service(service)
        _service = service()
        _service.init()
        self.__registry[service.__name__] = _service
        return _service

    @staticmethod
    def _ensure_valid_service(service):
        if not issubclass(service, BaseService):
            raise ServiceRegistryException('service must be subclass of BaseService')

    @classmethod
    def service(cls, service):
        return cls.instance().get(service)
