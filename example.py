import scigui

objects = [scigui.objects.Debug]
functions = [scigui.functions.AddNumbers, scigui.functions.Plot]

# Execute
app = scigui.Application(objects = objects, functions = functions)
app.run()
