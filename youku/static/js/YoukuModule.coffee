## coding: utf-8

class @YoukuModule
    constructor: (runtime, element, initArgs) ->
        @runtime = runtime
        @el = $(element)
        @el.data('name', 'YoukuModule')
        JavascriptLoader.executeModuleScripts(@el)

        new YKU.Player 'youkuplayer_${xblock_id}', {
            styleid: '0',
            client_id: '${app_id}',
            vid: '${file_id}'
        }

    $: (selector) ->
        $(selector, @el)
