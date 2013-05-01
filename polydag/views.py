from polydag.models import Node
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

import json

def getNode(req, nodeid, format):
    """
    GET .../<nodeid>
    => {
        'id' : int,
        'name' : str,
        'type' : str,
        'children' : list[{'id':int, 'name':str, 'type':str}, ...],
        ...
    }
    """
    if not format or len(format)==0:
        format = 'json' if req.is_ajax() else 'html'
    node = get_object_or_404(Node, pk=nodeid)
    return HttpResponse(json.dumps(node.to_dict(True)), content_type="application/json")


def list_tags(request, id):
    node = Node.objects.get(id=id)
    keys = [
                {'id':kw.pk, 'name':kw.name} for kw in node.keywords.all()
            ]
    return HttpResponse(json.dumps(keys), content_type="application/json")