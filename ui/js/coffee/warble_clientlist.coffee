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


nodeVal = (id, obj, t) ->
    if not document.getElementById("node_#{t}_tmp_#{id}")
        loc = obj.innerText
        obj.innerHTML = ""
        ip = new HTML('input', {style: { color: '#333', width: '320px', height: '24px', padding: '0px'}, data: loc, id: "node_#{t}_tmp_#{id}", type: 'text', onkeydown: "saveNodeValue(#{id}, this, event, '#{t}');", onblur: "savedNodeValue({}, {id: #{id}, type: '#{t}', #{t}: this.getAttribute('data')});"})
        ip.value = loc
        app(obj, ip)
        ip.focus()


saveNodeValue = (id, obj, e, t) ->
    if e.key == 'Enter'
        nval = obj.value
        js = {
            id: id
        }
        jsx = {
            id: id,
            type: t
        }
        js[t] = nval
        jsx[t] = nval
        post('node/modify', js, jsx, savedNodeValue)
    else if e.key == 'Escape'
        js = {id: id}
        jsx = {id: id, type: t}
        js[t] = obj.getAttribute('data')
        jsx[t] = obj.getAttribute('data')
        savedNodeValue(js, jsx)

savedNodeValue = (json, state) ->
    obj = document.getElementById("node_#{state.type}_#{state.id}")
    obj.innerHTML = ""
    app(obj, txt(state[state.type]))

# Node list sorting
nodeStatusSort = (a,b) =>
    # Favor enabled over not enabled
    return -1 if a.enabled and not b.enabled
    return 1 if b.enabled and not a.enabled
    
    # Favor verified over not verified
    return -1 if a.verified and not b.verified
    return 1 if b.verified and not a.verified
    
    # Fall back to hostname alpha-sort
    return a.hostname.localeCompare(b.hostname)

    
    
clientlist = (json, state) ->
    
    slist = mk('div')
    vlist = new HTML('div')
    if json.nodes
        sources = json.nodes
        sources = if sources.sort then sources else []
        sources.sort(nodeStatusSort)
        for source in sources
            
            card = new HTML('div', {class: 'clientcard'} )
            
            # node verified?
            banner = new HTML('div', {class: 'banner'})
            rline = new HTML('div', {style: { float: 'right', width: '300px', textAlign: 'center'}})
            lline = new HTML('div', {style: { float: 'left', width: '500px', textAlign: 'center'}})
            
            hn = new HTML('span', {title: 'Click to edit', id: "node_hostname_#{source.id}", onclick: "nodeVal(#{source.id}, this, 'hostname');"}, txt(source.hostname||"(unknown)"))
            
            lline.inject(hn)
            vrf = []
            if not source.verified
                card.setAttribute('class', 'clientcard orange')
                vrf = [
                    'Unverified Node',
                    new HTML('button', {class: 'btn btn-sm btn-primary', onclick: "modifyNode(#{source.id}, {verified: true, enabled: true});"}, "Verify + Enable")
                ]
                rline.inject(vrf)
                # delete btn
                btn = new HTML('button', {title: 'Delete node', class: 'btn btn-square btn-danger', style: {position: 'relative', float: 'right', display: 'inline-block'}, onclick: "deleteNode(#{source.id});"},
                               new HTML('i', {class: 'fa fa-trash'}, '')
                              )
                rline.inject(btn)
            
            # node enabled?
            if source.verified
                vrf = []
                card.setAttribute('class', 'clientcard green')
                if source.enabled
                    vrf = [
                        'Active',
                        new HTML('button', {class: 'btn btn-sm btn-warning', onclick: "modifyNode(#{source.id}, {enabled: false});"}, "Disable")
                    ]
                else
                    card.setAttribute('class', 'clientcard grey')
                    vrf = [
                        'Disabled',
                        new HTML('button', {class: 'btn btn-sm btn-primary', onclick: "modifyNode(#{source.id}, {enabled: true});"}, "Re-enable")
                    ]
                rline.inject(vrf)
                
                # delete btn
                btn = new HTML('button', {title: 'Delete node', class: 'btn btn-square btn-danger', style: {position: 'relative', float: 'right', display: 'inline-block'}, onclick: "deleteNode(#{source.id});"},
                               new HTML('i', {class: 'fa fa-trash'}, '')
                              )
                rline.inject(btn)
            
            banner.inject(lline)
            banner.inject(rline)
            
            card.inject(banner)
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
    
            
            # node fingerprint
            line = new HTML('div', {class: 'clientcardline'})
            line.inject( [
                new HTML('b', {}, "Fingerprint: "),
                new HTML('kbd', {title: "Run node.py --fingerprint if you need to re-check the fingerprint"}, source.fingerprint)
            ])
            d.inject(line)
            
            # node location
            line = new HTML('div', {class: 'clientcardline'})
            line.inject( [
                new HTML('b', {}, "Location: "),
                new HTML('span', {title: 'Click to edit', id: "node_location_#{source.id}", onclick: "nodeVal(#{source.id}, this, 'location');"}, txt(source.location||"(unknown)"))
            ])
            d.inject(line)
            
            # node description
            line = new HTML('div', {class: 'clientcardline'})
            line.inject( [
                new HTML('b', {}, "Notes: "),
                new HTML('span', {title: 'Click to edit', id: "node_description_#{source.id}", onclick: "nodeVal(#{source.id}, this, 'description');"}, txt(source.description||"(none)"))
            ])
            d.inject(line)
            
            # node last ping
            line = new HTML('div', {class: 'clientcardline'})
            lp = new Date(source.lastping*1000.0)
            now = new Date()
            line.inject( [
                new HTML('b', {}, "Last Active: "),
                txt(moment(lp).fromNow() + " (" + lp.ISOBare()  + ")")
            ])
            d.inject(line)
            
            # Check for inactive (dead?) nodes - only enabled ones, of course.
            if source.enabled and (moment(now).unix() - moment(lp).unix() > 900)
                card.setAttribute("class", "clientcard red")
                line.inject(txt(" - Node dead?!"))
                lline.inject(txt(" - (no contact for > 15 minutes!)"))
            
            
        
    #app(slist, tbl)
    state.widget.inject(slist, true)
    state.widget.inject(vlist)
    
    retval = mk('div')
    set(retval, 'id', 'retval')
    state.widget.inject(retval)
    showType(true) # Show first available type
    