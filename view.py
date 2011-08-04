#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ``RequestHandler``s.
"""

import cgi
import logging

from pytz.gae import pytz

from google.appengine.ext import blobstore, db

from weblayer import RequestHandler as BaseRequestHandler

import auth
import model

class RequestHandler(BaseRequestHandler):
    """
    """
    
    
    


class BlobStoreUploadHandler(RequestHandler):
    """ Base class for handlers that accept multiple named file uploads.
    """
    
    def __init__(self, *args, **kwargs):
        super(BlobStoreUploadHandler, self).__init__(*args, **kwargs)
        self._uploads = None
        
    
    def get_uploads(self):
        if self._uploads is None:
            self._uploads = {}
            for key, value in self.request.params.items():
                if isinstance(value, cgi.FieldStorage):
                    if 'blob-key' in value.type_options:
                        value = blobstore.parse_blob_info(value)
                        self._uploads[key] = value
        return self._uploads
        
    
    


class Index(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('index.tmpl')
        
    
    


class Standard(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('standard.tmpl')
        
    
    


class Download(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('download.tmpl')
        
    
    


class Support(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('support.tmpl')
        
    
    


class Contact(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('contact.tmpl')
        
    
    


class Library(RequestHandler):
    """
    """
    
    def get(self, name=None):
        
        # Get all `Series` so we can populate the category navigation and
        # the target `Series` if one has been selected.
        series = model.Series.get_all()
        if name is None:
            target = None
        else:
            target = model.Series.get_by_key_name(name)
        
        # Get either the most recent 9 `Design`s or the `Design`s in the
        # target `Series`.
        if target is None:
            designs = model.Design.all().order('-m').fetch(9)
        else:
            designs = target.designs
        
        # Render the template.
        return self.render(
            'library.tmpl', 
            series=series, 
            target=target, 
            designs=designs
        )
        
    
    


class AddDesign(BlobStoreUploadHandler):
    """
    """
    
    __all__ = ['get', 'post']
    
    @auth.required
    def post(self):
        
        attrs = {}
        
        params = self.request.params
        uploads = self.get_uploads()
        
        attrs['title'] = params.get('title')
        attrs['description'] = params.get('description')
        
        series = params.getall('series')
        attrs['series'] = [db.Key.from_path('Series', item) for item in series]
        
        country_code = self.request.headers.get('X-AppEngine-Country', 'GB')
        try:
            country = pytz.country_names[country_code.lower()]
        except KeyError:
            country = country_code
        attrs['country'] = country
        
        attrs.update(uploads)
        design = model.Design(**attrs)
        design.save()
        
        response = self.redirect('/library/design/%s' % design.key().id())
        response.body = ''
        return response
        
    
    
    @auth.required
    def get(self):
        series = model.Series.get_all()
        upload_url = blobstore.create_upload_url(self.request.path)
        return self.render('add.tmpl', upload_url=upload_url, series=series)
        
    
    


class AddDesignSuccess(BlobStoreUploadHandler):
    """
    """
    
    @auth.required
    def get(self):
        return {'status': 'ok'}
        
    
    


class Design(RequestHandler):
    """
    """
    
    def get(self, id):
        target = model.Design.get_by_id(int(id))
        series = model.Series.get_all()
        return self.render(
            'design.tmpl', 
            target=target, 
            series=series 
        )
        
    
    


class NotFound(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('errors/404.tmpl')
        
    
    


