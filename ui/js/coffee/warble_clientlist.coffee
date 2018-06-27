clientTypes = {}

showClientType = (t) ->
    for st, el of clientTypes
        if st == t or t == true
            t = "blargh"
            el.btn.className = "sourceTypeIcon selected"
            el.main.style.display = "block"
        else
            el.btn.className = "sourceTypeIcon"
            el.main.style.display = "none"


makeClientType = (main, t) ->
    if not clientTypes[t]
        obj = new HTML('div', { id: "client_#{t}", style: { display: "block" }})
        tbl = mk('table')
        set(tbl, 'class', 'table table-striped')
        thead = mk('thead')
        tr = mk('tr')
        for el in ['ID', 'IP', 'Hostname / Fingerprint', 'Location', 'Verified', 'Enabled', 'Last Ping',  'Actions']
            td = mk('th')
            if el.match(/Hostname/)
                td.style.width = "200px"
            if el.match(/Location/)
                td.style.minWidth = "300px"
            if el.match(/Actions/)
                td.style.minWidth = "240px"
            app(td, txt(el))
            app(tr, td)
        app(thead, tr)
        app(tbl, thead)
        
        tbody = new HTML('tbody')
        app(tbl, tbody)
        obj.inject(tbl)
        main.inject(obj)
        clientTypes[t] = {
            main: obj,
            div: tbody,
            count: 0
        }
    return clientTypes[t]

modifyNode = (id, stats) ->
    stats['id'] = id
    post('node/modify', stats, {}, location.reload())
    
deleteNode = (id, stats) ->
    if confirm('Are you sure you wish to delete this node?')
        xdelete('node/modify', {id: id}, {}, location.reload())

nodeLocation = (id, obj) ->
    if not document.getElementById("tnodeloc_#{id}")
        loc = obj.innerText
        obj.innerHTML = ""
        ip = new HTML('input', {style: { color: '#333', width: '320px', height: '24px', padding: '0px'}, data: loc, id: "tnodeloc_#{id}", type: 'text', onkeydown: "saveNodeLocation(#{id}, this, event);"})
        ip.value = loc
        app(obj, ip)
        ip.focus()
    

saveNodeLocation = (id, obj, e) ->
    if e.key == 'Enter'
        nloc = obj.value
        post('node/modify', { id: id, location: nloc}, {id: id, location: nloc}, savedNodeLocation)
    else if e.key == 'Escape'
        savedNodeLocation({}, {id: id, location: obj.getAttribute('data')})

savedNodeLocation = (json, state) ->
    obj = document.getElementById("nodeloc_#{state.id}")
    obj.innerHTML = ""
    app(obj, txt(state.location))
    
clientlist = (json, state) ->
    
    slist = mk('div')
    vlist = new HTML('div')
    if json.nodes
        sources = json.nodes
        sources = if sources.sort then sources else []
        sources.sort((a,b) => a.id - b.id)
        for source in sources
            
            card = new HTML('div', {class: 'clientcard'} )
            
            # node verified?
            d = new HTML('div', {height: '36px', position: 'relative', style: {marginBottom: '12px'}})
            
            line = new HTML('div', {style: { position: 'relative', lineHeight: '30px', height: '30px', float: 'left', padding: '2px',  display: 'inline-block', textAlign: 'center', margin: '-5.25px', width: '225px', borderTopLeftRadius: '6px', background: '#4c8946', marginBottom: '4px'}})
            vrf = []
            if not source.verified
                line.style.background = '#bc9621'
                card.style.borderColor = '#bc9621'
                line.style.width = '445px'
                vrf = [
                    'Unverified Node',
                    new HTML('button', {class: 'btn btn-sm btn-primary', onclick: "modifyNode(#{source.id}, {verified: true, enabled: true});"}, "Verify + Enable")
                ]
                line.inject(vrf)
                # delete btn
                btn = new HTML('button', {title: 'Delete node', class: 'btn btn-square btn-danger', style: {position: 'relative', float: 'right', display: 'inline-block'}, onclick: "deleteNode(#{source.id});"},
                               new HTML('i', {class: 'fa fa-trash'}, '')
                              )
                line.inject(btn)
                d.inject(line)
            
            # node enabled?
            if source.verified
                line = new HTML('div', {style: {position: 'relative', lineHeight: '30px', height: '30px', float: 'right', padding: '2px',display: 'inline-block', textAlign: 'center', margin: '-5.25px', width: '445px', borderTopRightRadius: '6px', background: '#4c8946', marginBottom: '4px'}})
                vrf = []
                card.style.borderColor = '#4c8946'
                if source.enabled
                    vrf = [
                        'Active',
                        new HTML('button', {class: 'btn btn-sm btn-warning', onclick: "modifyNode(#{source.id}, {enabled: false});"}, "Disable")
                    ]
                else
                    line.style.background = '#777'
                    card.style.borderColor = '#777'
                    vrf = [
                        'Disabled',
                        new HTML('button', {class: 'btn btn-sm btn-primary', onclick: "modifyNode(#{source.id}, {enabled: true});"}, "Re-enable")
                    ]
                line.inject(vrf)
                d.inject(line)
                
                # delete btn
                btn = new HTML('button', {title: 'Delete node', class: 'btn btn-square btn-danger', style: {position: 'relative', float: 'right', display: 'inline-block'}, onclick: "deleteNode(#{source.id});"},
                               new HTML('i', {class: 'fa fa-trash'}, '')
                              )
                line.inject(btn)
            
            
            
            
            card.inject(d)
            vlist.inject(card)
            
            d = new HTML('p')
            card.inject(d)
            
            # node ID
            line = new HTML('div', {class: 'clientcardline'})
            line.inject( [
                new HTML('b', {}, "Node ID: "),
                txt(source.id)
            ])
            d.inject(line)
            
            # node ip
            line = new HTML('div', {class: 'clientcardline'})
            line.inject( [
                new HTML('b', {}, "Node IP: "),
                txt(source.ip)
            ])
            d.inject(line)
            
            
            # node hostname
            line = new HTML('div', {class: 'clientcardline'})
            line.inject( [
                new HTML('b', {}, "Hostname: "),
                txt(source.hostname)
            ])
            d.inject(line)
            
            # node fingerprint
            line = new HTML('div', {class: 'clientcardline'})
            line.inject( [
                new HTML('b', {}, "Fingerprint: "),
                new HTML('kbd', {}, source.fingerprint)
            ])
            d.inject(line)
            
            # node location
            line = new HTML('div', {class: 'clientcardline'})
            line.inject( [
                new HTML('b', {}, "Location: "),
                new HTML('span', {id: "nodeloc_#{source.id}", onclick: "nodeLocation(#{source.id}, this, event);"}, txt(source.location||"(unknown)"))
            ])
            d.inject(line)
            
            
            
            d.inject(line)
            
            line.inject(new HTML('br'))
            line.inject(new HTML('br'))
            
            
            
            
        
    #app(slist, tbl)
    state.widget.inject(slist, true)
    state.widget.inject(vlist)
    
    retval = mk('div')
    set(retval, 'id', 'retval')
    state.widget.inject(retval)
    showType(true) # Show first available type
    