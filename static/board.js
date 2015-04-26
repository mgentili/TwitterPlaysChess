var INTERVAL = 5000;

var table = $('#example').DataTable( {
    "ajax" : {"url": SCRIPT_ROOT + 'get_counts'}
}    );

//table.on( 'xhr', function () {
//    var json = table.ajax.json();
//    console.log( json );
//});
    
setInterval( function () {
    table.ajax.reload();
    }, INTERVAL);



