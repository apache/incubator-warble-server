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
        for el in ['ID', 'IP', 'Hostname', 'Location', 'Verified', 'Enabled', 'Last Ping',  'Actions']
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

clientlist = (json, state) ->
    
    slist = mk('div')
    vlist = new HTML('div')
    if json.nodes
        st = makeClientType(vlist, 'node')
        sources = json.nodes
        sources = if sources.sort then sources else []
        sources.sort((a,b) => a.id - b.id)
        for source in sources
            tbody = st.div
            st.count++;
            
            d = mk('tr')
            set(d, 'id', source.id)
            set(d, 'scope', 'row')
            
            if source.verified == true
                d.style.fontWeight = 'bold'
            else
                d.style.color = '#942'
            
            if source.enabled == false
                d.style.fontStyle = 'italic'
                
            # node ID
            t = mk('td')
            app(t, txt(source.id.pad(3)))
            app(d, t)
            
            # node ip
            t = mk('td')
            app(t, txt(source.ip))
            app(d, t)
            
            
            # node hostname
            t = mk('td')
            app(t, txt(source.hostname))
            app(d, t)
            
            # node location
            t = mk('td')
            app(t, txt(source.location||"(unknown)"))
            app(d, t)
            
            # node verified?
            t = mk('td')
            t.style.color = if source.verified then "#393" else '#942'
            app(t, txt(if source.verified then '✓' else 'x'))
            app(d, t)
            
            # node enabled?
            t = mk('td')
            t.style.color = if source.enabled then "#393" else '#942'
            app(t, txt(if source.enabled then '✓' else 'x'))
            app(d, t)
            
            # node ping?
            t = mk('td')
            ts = new Date(source.lastping*1000.0).ISOBare() + " UTC"
            app(t, txt(ts))
            app(d, t)
            
            
            
            act = mk('td')
            
            # This only applies to verified nodes!
            if source.verified == true
                if source.enabled == false
                    # enable btn
                    dbtn = mk('button')
                    set(dbtn, 'class', 'btn btn-success')
                    set(dbtn, 'onclick', "modifyNode(#{source.id}, {enabled: true});")
                    dbtn.style.padding = "2px"
                    app(dbtn, txt("Enable"))
                    app(act, dbtn)
                else
                    # disable btn
                    dbtn = mk('button')
                    set(dbtn, 'class', 'btn btn-warning')
                    set(dbtn, 'onclick', "modifyNode(#{source.id}, {enabled: false});")
                    dbtn.style.padding = "2px"
                    app(dbtn, txt("Disable"))
                    app(act, dbtn)
                
            if source.verified == false
                # verify btn
                dbtn = mk('button')
                set(dbtn, 'class', 'btn btn-primary')
                set(dbtn, 'onclick', "modifyNode(#{source.id}, {verified: true});")
                dbtn.style.padding = "2px"
                app(dbtn, txt("Verify"))
                app(act, dbtn)
            
                
            
            
            # delete btn
            dbtn = mk('button')
            set(dbtn, 'class', 'btn btn-danger')
            set(dbtn, 'onclick', "deleteNode(#{source.id});")
            dbtn.style.padding = "2px"
            app(dbtn, txt("Delete"))
            app(act, dbtn)
            
            app(d, act)
            tbody.inject(d)
        
    #app(slist, tbl)
    state.widget.inject(slist, true)
    state.widget.inject(vlist)
    
    retval = mk('div')
    set(retval, 'id', 'retval')
    state.widget.inject(retval)
    showType(true) # Show first available type
    