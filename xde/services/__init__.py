# Copyright (C) 2015 Xomad. All rights reserved.
#
# This software is the confidential and proprietary information of
# Xomad or one of its subsidiaries. You shall not disclose this
# confidential information and shall use it only in accordance with
# the terms of the license agreement or other applicable agreement you
# entered into with Xomad.
#
# XOMAD MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE
# SUITABILITY OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT. XOMAD
# SHALL NOT BE LIABLE FOR ANY LOSSES OR DAMAGES SUFFERED BY LICENSEE
# AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
# DERIVATIVES.
#
# Created on 22/10/2015


class ServiceErrorException(Exception):
    pass


class ServiceRateLimitException(Exception):
    pass


class BaseService(object):
    @property
    def name(self):
        return self.__class__.__name__

    def init(self):
        """Override this method to initialize service"""
        pass

    def shutdown(self):
        """Override this method to shutdown service gracefully"""
        pass
