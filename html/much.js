
angular.module('LunApp', [])
.config( [
    '$compileProvider',
    function( $compileProvider )
    {
      $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|vlc):/);
    }
])

.controller('FilmCtrl', function($scope, $http){
  
  $scope.decodeURL = decodeURIComponent;
  
  $scope.domain = document.domain;
  
  var films = $scope.films = [];
  $http({
    headers: {'Content-Type': 'application/json'},
    url: '/cgi-bin/lmdb/get_films.py',
    method: "GET",
    params: {
    }
  })
  .success(function(data){
    films = $scope.films = data;
  });
  
  
  getPositionRatio = function(element){
    var y = Math.max((element.getBoundingClientRect().top + element.getBoundingClientRect().bottom)/2, 0)
    var height = Math.max(document.documentElement.clientHeight, window.innerHeight || 0)
    return 2*Math.min(height-y, y)/height;
  }
  
  window.onscroll = function(event){
/*    for (var i = 0; i<films.length; i++){
      var element = document.getElementById(films[i].id);
      var height = getPositionRatio(element);
      element.style.height = 150*height + ' px';
      element.style.maxWidth = 150*height + ' px';
    }*/
  }
  
  
  $scope.displayed_film = null;
  
  $scope.display = function(film){
    $scope.displayed_film = film;
    
    $http({
      headers: {'Content-Type': 'application/json'},
      url: '/cgi-bin/lmdb/list_files_json.py',
      method: "GET",
      params: {
        'path': film.pathname
      }
    })
    .success(function(data){
      $scope.listing = data;
    });
    
  }
  
 
  $scope.year_interval = function(film){
    if (film.type == 'movie')
      return film.start_year
    else if (film.end_year == null)
      return film.start_year + '-'
    else
      return film.start_year + '-' + film.end_year
  }
  
  $scope.evalUserMeter = function(tomatousermeter){
    if (tomatousermeter < 50){
      return "negative";
    }
    return "positive";
  }
  
  $scope.evalMetascore = function(metascore){
    if (metascore > 60)
      return "#6C3"; // Green
    
    else if (metascore >= 40)
      return "#FC3"; // Yellow
    
    return "#F00"; // Red
  }
  
});
