#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-10-10 17:32
# @Author  : Jieay
# @File    : views.py
from __future__ import absolute_import, unicode_literals
from importlib import import_module
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
# from django.utils.six.moves import urllib_parse
from urllib import parse as urllib_parse
from django.utils.translation import ugettext_lazy as _
from django_cas_ng.models import ProxyGrantingTicket, SessionTicket
from django_cas_ng.signals import cas_user_logout
from django_cas_ng.utils import (
    get_cas_client,
    get_protocol,
    get_redirect_url,
    get_service_url,
)
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

from django_cas_ng.views import LoginView, LogoutView, clean_sessions
from rest_framework.authtoken.models import Token

import logging
logger = logging.getLogger(__name__)


class CasLoginView(LoginView):
    def successful_login(self, request, next_page):
        """
        This method is called on successful login. Override this method for
        custom post-auth actions (i.e, to add a cookie with a token).

        :param request: WSGIRequest
        :param next_page:
        :return:
        """
        user = request.user
        logger.info('check user: {}'.format(user))
        token_obj = Token.objects.filter(user=user)
        if token_obj.exists():
            token = token_obj[0].key
        else:
            token = None
        logger.info('Token: {}'.format(token))
        session_key = request.session.session_key
        # logger.info('Login request.COOKIES: {}'.format(request.COOKIES))
        # logger.info('Login request.session: {}'.format(request.session))
        # get_coolies = request.COOKIES
        # csrftoken = get_coolies.get('csrftoken')
        if token is not None:
            new_next_page = '{}?token={}&session_key={}'.format(next_page, token, session_key)
            # if settings.DEBUG:
            #     new_next_page = '{}?csrftoken={}&sessionid={}&token={}'.format(
            #         next_page, csrftoken, sessionid, token
            #     )
        else:
            new_next_page = next_page
        logger.info('next_page: {}'.format(new_next_page))

        return HttpResponseRedirect(new_next_page)

    def post(self, request):
        if request.POST.get('logoutRequest'):
            next_page = request.POST.get('next', settings.CAS_REDIRECT_URL)
            service_url = get_service_url(request, next_page)
            client = get_cas_client(service_url=service_url, request=request)

            clean_sessions(client, request)
            return HttpResponseRedirect(next_page)

    def get(self, request):
        """
        Forwards to CAS login URL or verifies CAS ticket

        :param request:
        :return:
        """
        next_page = request.GET.get('next')
        required = request.GET.get('required', False)

        service_url = get_service_url(request, next_page)
        # logger.info('service_url: {}'.format(service_url))
        client = get_cas_client(service_url=service_url, request=request)

        if not next_page and settings.CAS_STORE_NEXT and 'CASNEXT' in request.session:
            next_page = request.session['CASNEXT']
            del request.session['CASNEXT']

        if not next_page:
            next_page = get_redirect_url(request)

        if request.user.is_authenticated:
            if settings.CAS_LOGGED_MSG is not None:
                message = settings.CAS_LOGGED_MSG % request.user.get_username()
                messages.success(request, message)
                logger.info('user is authenticated')
                user = request.user
                Token.objects.update_or_create(user=user)
            return self.successful_login(request=request, next_page=next_page)

        ticket = request.GET.get('ticket')
        logger.info('Login ticket: {}'.format(ticket))
        if ticket:
            user = authenticate(ticket=ticket,
                                service=service_url,
                                request=request)
            logger.info('ticket user: {}'.format(user))
            # print('user:', type(user))
            pgtiou = request.session.get("pgtiou")
            if user is not None:
                if not request.session.exists(request.session.session_key):
                    request.session.create()
                auth_login(request, user)
                SessionTicket.objects.create(
                    session_key=request.session.session_key,
                    ticket=ticket
                )
                Token.objects.update_or_create(user=user)

                if pgtiou and settings.CAS_PROXY_CALLBACK:
                    # Delete old PGT
                    ProxyGrantingTicket.objects.filter(
                        user=user,
                        session_key=request.session.session_key
                    ).delete()
                    # Set new PGT ticket
                    try:
                        pgt = ProxyGrantingTicket.objects.get(pgtiou=pgtiou)
                        pgt.user = user
                        pgt.session_key = request.session.session_key
                        pgt.save()
                    except ProxyGrantingTicket.DoesNotExist:
                        pass

                if settings.CAS_LOGIN_MSG is not None:
                    name = user.get_username()
                    message = settings.CAS_LOGIN_MSG % name
                    messages.success(request, message)
                return self.successful_login(request=request, next_page=next_page)
            elif settings.CAS_RETRY_LOGIN or required:
                return HttpResponseRedirect(client.get_login_url())
            else:
                raise PermissionDenied(_('Login failed.'))
        else:
            if settings.CAS_STORE_NEXT:
                request.session['CASNEXT'] = next_page
            return HttpResponseRedirect(client.get_login_url())


class CasLogoutView(LogoutView):
    def get(self, request):
        """
        Redirects to CAS logout page

        :param request:
        :return:
        """
        next_page = request.GET.get('next')
        token = request.GET.get('token')
        session_key = request.GET.get('session_key')

        print('token: {} session_key: {}'.format(token, session_key))
        # try to find the ticket matching current session for logout signal
        try:
            st = SessionTicket.objects.get(session_key=session_key)
            ticket = st.ticket
        except SessionTicket.DoesNotExist:
            ticket = None
        # send logout signal
        # print('request.COOKIES: {}'.format(request.COOKIES))
        # print('request.session: {}'.format(request.session))
        logger.info('request.user: {}'.format(request.user))
        logger.info('logout ticket: {}'.format(ticket))
        logger.info('Start cas logout.')
        cas_user_logout.send(
            sender="manual",
            user=request.user,
            session=request.session,
            ticket=ticket,
        )
        logger.info('Start sys logout.')
        auth_logout(request)
        # clean current session ProxyGrantingTicket and SessionTicket
        ProxyGrantingTicket.objects.filter(session_key=session_key).delete()
        SessionTicket.objects.filter(session_key=session_key).delete()
        Token.objects.filter(key=token).delete()

        next_page = next_page or get_redirect_url(request)
        logger.info('Logout next_page: {}'.format(next_page))
        if settings.CAS_LOGOUT_COMPLETELY:
            protocol = get_protocol(request)
            host = request.get_host()
            redirect_url = urllib_parse.urlunparse(
                (protocol, host, next_page, '', '', ''),
            )
            logger.info('Logout redirect_url: {}'.format(redirect_url))
            client = get_cas_client(request=request)
            # logger.info('Logout client.get_logout_url(redirect_url): {}'.format(client.get_logout_url(redirect_url)))
            return HttpResponseRedirect(client.get_logout_url(next_page))
        else:
            # This is in most cases pointless if not CAS_RENEW is set. The user will
            # simply be logged in again on next request requiring authorization.
            return HttpResponseRedirect(next_page)