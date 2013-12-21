from polydag.management.commands.graphviz import Command
from documents.models import Page
Command.COLORS['Course'] = 'purple'
Command.COLORS['Thread'] = 'green'
Command.COLORS['Document'] = 'yellow'
Command.EXCLUDE.append(Page)
