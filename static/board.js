var INTERVAL = 5000;

var table = $('#example').DataTable( {
    "ajax" : {"url": SCRIPT_ROOT + 'get_counts'},
    "order" : [[ 1, "desc" ]]
}    );

    
setInterval( function () {
    table.ajax.reload();
    console.log("Setting table");
    }, INTERVAL);



