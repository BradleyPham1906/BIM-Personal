  /* ================= __acad3dV135: find open data ================= */
  /* US open-data portals, [group, [[name, host, Hub site id, ArcGIS organisation id, Socrata], ...]].
     The list, and the searches below, are ported from GeoLibre (github.com/opengeos/GeoLibre):
       MIT License
       Copyright (c) 2026 Qiusheng Wu
       Permission is hereby granted, free of charge, to any person obtaining a copy of this software
       and associated documentation files (the "Software"), to deal in the Software without
       restriction, including without limitation the rights to use, copy, modify, merge, publish,
       distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
       Software is furnished to do so, subject to the following conditions:
       The above copyright notice and this permission notice shall be included in all copies or
       substantial portions of the Software.
       THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
       BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
       NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
       DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
       OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. */
  var BIM_DATA_PORTALS=[["Federal: Department of Agriculture",[["Aerial Photography Field Office (NAIP)","apfo-usdaonline.opendata.arcgis.com","f77cc8e92add4eb4b76b1aadfde7e12d","LLVEmB8Lsae3Um4s",0],["Forest Service","data-usfs.hub.arcgis.com","4f29e28b4c0b4a52a512e7106dd1245e","gGHDlz6USftL5Pau",0],["Natural Resources Conservation Service","nrcs.maps.arcgis.com","","SXbDpmb7xQkk44JV",0],["USDA Geospatial Hub","gisforagriculture-usdaocio.hub.arcgis.com","841d7b85b009467e92362a936a3da9d9","5vMtpwj1mnc06Rmi",0]]],["Federal: Department of Commerce",[["Census Bureau","uscensus.maps.arcgis.com","","DlJzJLOZpPXmMpWi",0],["NOAA GeoPlatform","noaa.maps.arcgis.com","","C8EMgrsFcRFL6LrL",0],["NOAA Marine Cadastre","hub.marinecadastre.gov","7483257320154fb9b1e3d5ee14209e9d","C8EMgrsFcRFL6LrL",0]]],["Federal: Department of Defense",[["Army Corps of Engineers","geospatial-usace.opendata.arcgis.com","b3ac9c3c3e0744f2a3d17f69124c5726","n1YM8pTrFmm7L4hs",0],["National Geospatial-Intelligence Agency","nga.maps.arcgis.com","","cc7nIINtrZ67dyVJ",0]]],["Federal: Department of Energy",[["EIA U.S. Energy Atlas","atlas.eia.gov","a0dfa553e2b04b6bbf1ab9cf5dfb0353","FGr1D95XCGALKXqM",0]]],["Federal: Department of Homeland Security",[["FEMA","gis-fema.hub.arcgis.com","459129cb5e734aa984441f431f440613","XG15cJAlne2vxtgt",0]]],["Federal: Department of Housing and Urban Development",[["HUD Open Data","hudgis-hud.opendata.arcgis.com","0763b052200247aabeafe1abfbfb5afa","VTyQ9soqVukalItT",0]]],["Federal: Department of the Interior",[["Bureau of Land Management","gbp-blm-egis.hub.arcgis.com","1f7469023a92437a8a7e2dd7d8ba808a","KbxwQRRfWyEYLgp4",0],["Bureau of Ocean Energy Management","boem-metaport-boem.hub.arcgis.com","8279102fae2d40e283f8e0759e6adcc8","G5Ma95RzqJRPKsWL",0],["Fish and Wildlife Service","gis-fws.opendata.arcgis.com","a8358715b5214164a6db8024e838febd","QVENGdaPbd4LUkLV",0],["National Interagency Fire Center","data-nifc.opendata.arcgis.com","3b52b3585ac341a69a92a366db96e7ef","T4QMspbfLg3qTGWY",0],["National Park Service","public-nps.opendata.arcgis.com","a8c34bbc96934f528e38fbb45093cdb6","fBc8EJBxQRMcHlei",0],["U.S. Geological Survey","usgs.maps.arcgis.com","","v01gqwM5QqNysAAi",0]]],["Federal: Department of Transportation",[["BTS Geospatial (NTAD)","geodata.bts.gov","7b0390bcff3942e9956a4ad837c86a04","xOi1kZaI0eWDREZv",0],["FAA Aeronautical Data","adds-faa.opendata.arcgis.com","96a460b685d2408892b61bb2a45c166c","ssFJjBXIUyZDrSYZ",0]]],["Federal: Environmental Protection Agency",[["U.S. EPA","epa.maps.arcgis.com","","cJ9YHowT8TU7DUyn",0]]],["Federal: Multi-agency",[["Esri U.S. Federal Datasets","fedmaps.maps.arcgis.com","","FiaPA4ga0iQKduv3",0],["GeoPlatform (NGDA)","geoplatform.maps.arcgis.com","","Hp6G80Pky0om7QvQ",0]]],["Federal: NASA",[["NASA ArcGIS Online","nasa.maps.arcgis.com","","WSiUmUhlFx4CtMBB",0]]],["Alabama: state",[["Alabama GeoHub","data-algeohub.opendata.arcgis.com","01ed721f8ff54258885462f2d67b6d12","jF2q3LPxL7PETdYk",0]]],["Alabama: cities and counties",[["Jefferson County (Birmingham)","data-jeffco-al.opendata.arcgis.com","01f85376565647d385c7dbc702e372af","2FZPLYt8NeStZfN0",0]]],["Alaska: state",[["Alaska Geoportal","akgeoportal.alaska.gov","7dd7c86dd0cc40f6a516eb77001977c1","7HDiw78fcUiM2BWn",0],["Alaska DOT&PF Open Data","data-soa-akdot.opendata.arcgis.com","a135226f45964bce9e40684931bd451a","r4A0V7UzH9fcLVvv",0]]],["Arizona: state",[["AZGeo Data Hub","azgeo-data-hub-agic.hub.arcgis.com","7b373aac2d1f449886c3c5f25154bd14","MrgGZS7oC7drh1E8",0]]],["Arizona: cities and counties",[["Chandler","share-open-data-changis.hub.arcgis.com","fe9b58eeda704c7da2894f50e2bf48eb","HIBNcuytta1apnkB",0],["Maricopa County","data-maricopa.opendata.arcgis.com","99e683720a984c64b99ff5b6db48b06c","ykpntM6e3tHvzKRJ",0],["Mesa","data.mesaaz.gov","","",1],["Phoenix","mapping-phoenix.opendata.arcgis.com","a5bb48923e424bc69529f759146bbafd","cfKakmeHE95cgeEK",0],["Pima County","gisopendata.pima.gov","d8f0599e6dd14fd69a00d982ad4fd985","UTBp78iglGpbqp1B",0],["Scottsdale","data.scottsdaleaz.gov","a6371d6040274c2a8a0020e68fe6059f","hvDuIN6e7bxkHpdO",0],["Tempe","data.tempe.gov","2722e04735c84b3db11b63135d1f161f","lQySeXwbBg53XWDi",0],["Tucson","gisdata.tucsonaz.gov","c069f7b3210640e6bb31ae2adbeda9fe","9coHY2fvuFjG9HQX",0]]],["Arkansas: state",[["Arkansas GIS Hub","geodata.gis.arkansas.gov","34a99801c7f9458b9cf268759e38b8e3","PwY9ZuZRDiI5nXUB",0]]],["California: state",[["California State Geoportal","gis.data.ca.gov","cf412a17daaa47bca93c6d6b7e77aff0","uknczv4rpevve42E",0]]],["California: cities and counties",[["Alameda County","data.acgov.org","6b8917a95a694c1b93750d03a05d7b72","ROBnTHSNjoZ2Wm1P",0],["Berkeley","data.cityofberkeley.info","","",1],["Fresno","gis-cityoffresno.hub.arcgis.com","070c879d03f94cd38e1fd4d3537eecb0","WkBUojyNPhsWOk1W",0],["Irvine","city-of-irvine-open-data-portal-cityofirvine.hub.arcgis.com","1183f17528c0457aa7886cbb8a8d2e34","3mkVbLdbLBFHrfbK",0],["Long Beach","datalb.longbeach.gov","5f5a5ce5987b438bae2a4d98158c00fb","yCArG7wGXGyWLqav",0],["Los Angeles County eGIS","egis-lacounty.hub.arcgis.com","4406d6e5e99345078342e91082e517a0","RmCCgQtiZLDCtblq",0],["Los Angeles County Open Data","data.lacounty.gov","ade02d0e6aa44df5bc3c9994c827c744","RmCCgQtiZLDCtblq",0],["Los Angeles GeoHub","geohub.lacity.org","e51ee91017d940c1be47fa639906bfe7","7nsPwEMP38bSkCjy",0],["Los Angeles Open Data","data.lacity.org","","",1],["Marin County","data.marincounty.gov","","",1],["Oakland","data.oaklandca.gov","","",1],["Orange County","data-ocpw.opendata.arcgis.com","701e29e22a9740029a3fa6139810f80a","UXmFoWC7yDHcDN5Q",0],["Riverside County","gisopendata-countyofriverside.opendata.arcgis.com","d7050d61bdbd4a7c807d3624c35ec64f","pWmBUdSlVpXStHU6",0],["Sacramento","data.cityofsacramento.org","bca1167f95b64534b8717a1895313a4e","54falWtcpty3V47Z",0],["Sacramento County","data.saccounty.gov","1a43a893ae944983a6ca23548da3b072","5NARefyPVtAeuJPU",0],["San Bernardino County","open-data-sbcounty.hub.arcgis.com","9f65b78ad1d948c79be169eb8833da53","aA3snZwJfFkVyDuP",0],["San Diego County","data.sandiegocounty.gov","","",1],["San Francisco","data.sf.gov","","",1],["San Jose","gisdata-csj.opendata.arcgis.com","328f7cf06fc243e0a974b4b4b7aa2398","6kSayNlqm3HvsYZ8",0],["San Mateo County","data.smcgov.org","","",1],["Santa Clara County","data.sccgov.org","","",1],["Santa Monica","gisdata.santamonica.gov","9a2a5d77633e44c5863a9660d709a9e1","ntb1ZybmOdA9GyKm",0],["Sonoma County","data.sonomacounty.ca.gov","","",1],["West Hollywood","data.weho.org","","",1]]],["Colorado: state",[["Colorado Geospatial Portal","geodata.colorado.gov","ad44998e71504069b225d1a34174616f","DgjqnJA1rgO92Soi",0],["CDOT Open Data","data-cdot.opendata.arcgis.com","8dc5e19e1be5444f82b730a630fc49e2","yzB9WM8W0BO3Ql7d",0]]],["Colorado: cities and counties",[["Aurora","data-auroraco.opendata.arcgis.com","af35aff0c1b84d98829031a57a77bdbb","0Va1ID99NSrNyyPX",0],["Boulder","open-data.bouldercolorado.gov","4ce1e35aa122446caf541b7179f3e8c9","ePKBjXrBZ2vEEgWd",0],["Denver","opendata-geospatialdenver.hub.arcgis.com","08ac95d2733c45059ec5a3c76faa770d","zdB7qR0BtYrg0Xpl",0],["El Paso County (Colorado Springs)","opendata-elpasoco.hub.arcgis.com","755cb06024d84559b3068d022f98a97f","r1Gf4AJYRBIM0N25",0],["Fort Collins","opendata.fcgov.com","","",1]]],["Connecticut: state",[["CT Geospatial Data Portal","geodata.ct.gov","326277d68c5942c09cd9435eafb0aad4","3FL1kr7L4LvwA2Kb",0],["CT DEEP GIS Open Data","ct-deep-gis-open-data-website-ctdeep.hub.arcgis.com","034830942319469580596f12caf0284b","FjPcSmEFuDYlIdKC",0]]],["Connecticut: cities and counties",[["Hartford","open-data-hartford-hartfordgis.hub.arcgis.com","09f51357187b444c95d3c339fc05245a","WM6ZNcwewSWH8Mo9",0]]],["Delaware: state",[["Delaware FirstMap","de-firstmap-delaware.hub.arcgis.com","31b1cca8e69f4dcdad1e5325a98a180b","bFDgLqS5IyUBQLAd",0]]],["District of Columbia: state",[["Open Data DC","opendata.dc.gov","b907a83b8d3947bb8e318a7b93abadf8","neT9SoYxizqTHZPH",0]]],["Florida: state",[["Florida Geospatial Open Data Portal","geodata.floridagio.gov","7386e1cfa2994976a9b91f3c1cd0f044","Gh9awoU677aKree0",0],["Florida DEP Geospatial Open Data","geodata.dep.state.fl.us","841cd28db0ff4c81a364cdb1d4319cf5","nRHtyn3uE1kyzoYc",0],["FDOT Open Data","gis-fdot.opendata.arcgis.com","af8f7d9ac0584685a6cd835d84e0ec7d","O1JpcwDW8sjYuddV",0]]],["Florida: cities and counties",[["Broward County","geohub-bcgis.opendata.arcgis.com","27302957e4714e1abbb9753cd7042520","JMAJrTsHNLrSsWf5",0],["Gainesville","data.cityofgainesville.org","","",1],["Miami","datahub-miamigis.opendata.arcgis.com","8b9b67f78e1c4b8fb8073b05d9bdc2a5","CvuPhqcTQpZPT9qY",0],["Miami-Dade County","gis-mdc.opendata.arcgis.com","d2e3d8b28e74451bbd1db16e1f577e60","8Pc9XBTAsYuxx9Ny",0],["Orlando","data.cityoforlando.net","","",1],["Palm Beach County","opendata2-pbcgov.opendata.arcgis.com","a1b6b8c47ba74bdf96506d2ee331e7ac","ZWOoUZbtaYePLlPw",0],["St. Petersburg","geohub-csp.opendata.arcgis.com","aa0d8876a64444d687c9028bce388366","9qPLjNtocjo438CJ",0],["Tallahassee-Leon County","geodata-tlcgis.opendata.arcgis.com","2809d608961543cf918be6587b975f01","ptvDyBs1KkcwzQNJ",0],["Tampa","city-tampa.opendata.arcgis.com","316ee3c5e5ef40bc84694258182d94f3","IbNXlmt2RVVRCZ6M",0]]],["Georgia: state",[["Georgia GIO","data-hub.gio.georgia.gov","","Za9Nk6CPIPbvR1t7",0],["Georgia DCA","data-georgia-dca.opendata.arcgis.com","f0287e619f584bc5bcdb7621ead061f8","Gqyymy5JISeLzyNM",0]]],["Georgia: cities and counties",[["Athens-Clarke County","data-athensclarke.opendata.arcgis.com","5933dee3d8ec482db975644976db96de","xSEULKvB31odt3XQ",0],["Atlanta Regional Commission","opendata.atlantaregional.com","0baf04b4a2c64480be1beac144560262","Ug5xGQbHsD8zuZzM",0],["DeKalb County","dcgis-dekalbgis.hub.arcgis.com","533d0bcf1d4343d5b279ea35143b52c5","IxVN2oUE9EYLSnPE",0],["Gwinnett County","gcgis-gwinnettcountyga.hub.arcgis.com","8ef19395d08f42c495d53ce6bfbb3850","RfpmnkSAQleRbndX",0]]],["Hawaii: state",[["Hawaii Statewide GIS Program","geoportal.hawaii.gov","4c589a11a46d4514b9b6b081c5220b4a","HQ0xoN0EzDPBOEci",0]]],["Hawaii: cities and counties",[["Honolulu GIS","honolulu-cchnl.opendata.arcgis.com","8e80ac7782c1415baf3346b2d07ac493","tNJpAOha4mODLkXz",0],["Honolulu Open Data","data.honolulu.gov","","",1]]],["Idaho: state",[["State of Idaho GIS","gis-idaho.hub.arcgis.com","fa79cf3d606942148117507a3a421ba4","CNPdEkvnGl65jCX8",0]]],["Idaho: cities and counties",[["Boise","opendata.cityofboise.org","ee109a20969d4317918cfead374dbb2f","WHM6qC35aMtyAAlN",0]]],["Illinois: state",[["IDOT Open Data","gis-idot.opendata.arcgis.com","be6d60db78c642cc9d43e72f2fe83af8","aIrBD8yn1TDTEXoz",0]]],["Illinois: cities and counties",[["Chicago","data.cityofchicago.org","","",1],["Cook County GIS","hub-cookcountyil.opendata.arcgis.com","2a191092b4de474883802824e9593ffa","I5Or36sMcO7Y9vQ3",0],["Cook County Open Data","datacatalog.cookcountyil.gov","","",1],["Naperville","data.naperville.il.us","68c4ed288a9d43b0a504c742885e7f06","rXJ6QApc2sOtl1Pd",0]]],["Indiana: state",[["IndianaMap","www.indianamap.org","c470d38a730b4a5d839602174ed97d5c","fAJUAyCk5qmGxuxo",0]]],["Indiana: cities and counties",[["Bloomington","data.bloomington.in.gov","","",1],["Hamilton County","geohub.hamiltoncounty.in.gov","e1e638229287427eb85a94e23c690fc2","beYj0ONLvCt8qxHA",0],["Indianapolis","data.indy.gov","7753aa0e70414d92bce4b29dc9313011","xBsPUWYKO89lShIO",0]]],["Iowa: state",[["Iowa Geospatial Data","geodata.iowa.gov","463693b7d3bc449eb44d427c68db1c87","vPD5PVLI6sfkZ5E4",0],["Iowa DOT Open Data","data.iowadot.gov","167854bb9ecb40e191c8e5919dd143de","8lRhdTsQyJpO52F1",0]]],["Kansas: state",[["Kansas Geoportal","hub.kansasgis.org","1dfeade4e1e046dd8fa683d39dc3aa75","q2CglofYX6ACNEeu",0]]],["Kansas: cities and counties",[["Johnson County","jocogov-aims.opendata.arcgis.com","40721007a46645068b3ddc58f3ab7054","VI7SIDfzMs53TTMm",0],["Olathe","data-cityofolathe.opendata.arcgis.com","6687ef797a85482eb86164f2ecedae1d","V5kJ9QPOiI1K62Ac",0],["Sedgwick County","sedgwick-county-gis-sedgwickcounty.hub.arcgis.com","d7b2326339b34d33bae6db68e9d50594","McLat6HlPl45bNBv",0],["Wichita","data-cityofwichita.hub.arcgis.com","5a479578cbd1446b8a3e58d004fcb794","lOHEurd1BgncOSk1",0]]],["Kentucky: state",[["KyGovMaps Open Data","opengisdata.ky.gov","31ace50dd2204932b8b11c48f24f6e76","ghsX9CKghMvyYjBU",0],["KyFromAbove","kyfromabove.ky.gov","c8be0e1e0cbc44dd8201198cf92dcad6","ghsX9CKghMvyYjBU",0]]],["Kentucky: cities and counties",[["Lexington","data-lfucg.hub.arcgis.com","87de3890a26e41a7bd54752ef1699f98","Mg7DLdfYcSWIaDnu",0],["Louisville","data.louisvilleky.gov","105d192e2725465fa5ff70d163ca457a","79kfd2K6fskCAkyg",0]]],["Louisiana: state",[["Louisiana DOTD","release-ladotd.hub.arcgis.com","","PLiuXYMBpMK5h36e",0],["Atlas: The Louisiana Statewide GIS","atlas-lsuga.opendata.arcgis.com","","SDQDNhpG8jikA0D1",0]]],["Louisiana: cities and counties",[["Baton Rouge","data.brla.gov","","",1],["New Orleans","data.nola.gov","","",1]]],["Maine: state",[["Maine GeoLibrary","mainegeolibrary-maine.hub.arcgis.com","c0525bd8d13b4637a352684867faf162","RbMX0mRVOFNTdLzd",0]]],["Maryland: state",[["Maryland GIS Data Catalog","data.imap.maryland.gov","27d04aff6b9b426ab3c68eee68c23589","njFNhDsUCentVYJW",0]]],["Maryland: cities and counties",[["Baltimore","data.baltimorecity.gov","bb5a4d421ed64feeb4c3c879dede44f2","UWYHeuuJISiGmgXx",0],["Baltimore County","opendata.baltimorecountymd.gov","6df978664d834dcfa43c84503d040e1b","Ynpzre7M7vSGY7dh",0],["Montgomery County","data.montgomerycountymd.gov","","",1],["Prince George's County","data.princegeorgescountymd.gov","","",1]]],["Massachusetts: state",[["MassGIS Data Hub","gis.data.mass.gov","d36b7fc5ca494d2dac2cf03659b7647f","hGdibHYSPO59RG1h",0],["MassDOT Open Data","geo-massdot.opendata.arcgis.com","a302d9368ea648979a2df877a5a595b1","ceiitspzDAHrdGO1",0]]],["Massachusetts: cities and counties",[["Boston","bostonopendata-boston.opendata.arcgis.com","f23bac8afcd343f1a24a7e26d8d2bf96","sFnw0xNflSi8J0uh",0],["Cambridge","data.cambridgema.gov","","",1]]],["Michigan: state",[["State of Michigan Open Data","gis-michigan.opendata.arcgis.com","c486626179134b8093f21043f7d689c3","dxRQUfTDNtfqZ301",0]]],["Michigan: cities and counties",[["Detroit","data.detroitmi.gov","c4f0193f90d44ec7a59236d681a74dbb","qvkbeam7Wirps6zC",0]]],["Minnesota: state",[["Minnesota Geospatial Commons","gis.data.mn.gov","a5be19f6b69c46a3b4ae3669db4679c3","9OIuDHbyhmH91RfZ",0]]],["Minnesota: cities and counties",[["Hennepin County","gis-hennepin.hub.arcgis.com","05cd4c5cbdb8413a9258cc24f5d19224","ziLNoRgqnICUM0q1",0],["Minneapolis","opendata.minneapolismn.gov","c74e041718394d85bb291822c415f46b","afSMGVsC7QlRK1kZ",0],["St. Paul","information.stpaul.gov","1e2bdd73bc384d70aea7a337ba0cd3ce","9meaaHE3uiba0zr8",0]]],["Mississippi: state",[["Mississippi Geospatial Data Catalog","opendata.gis.ms.gov","b5bc97fd399b4d0e9364335bec6c816d","XSDoE9o9b2LpxKKd",0]]],["Missouri: state",[["MSDIS","data-msdis.opendata.arcgis.com","466c4ea412064d2a95997c79b4580529","kNS2ppBA4rwAQQZy",0]]],["Missouri: cities and counties",[["Columbia","datahub-gocolumbiamo.opendata.arcgis.com","adaa409fd4814ebabe212fdb818b944a","GHhNHT1xiCkCAXvo",0],["Kansas City","data.kcmo.org","","",1]]],["Montana: state",[["Montana Geographic Information","montana-state-library-2022-floods-gis-data-hub-montana.hub.arcgis.com","","qnjIrwR8z5Izc0ij",0],["Montana FWP","gis-mtfwp.hub.arcgis.com","9e84bea7a01448dda660470fd1bb792e","Cdxz8r11hT0MGzg1",0]]],["Nebraska: state",[["NebraskaMAP","www.nebraskamap.gov","fe5b9beb17674749ba5769f368ef60af","Sj9eBhzWwOMzQCfI",0]]],["Nebraska: cities and counties",[["Omaha-Douglas County","data-dogis.opendata.arcgis.com","31381668ca6f490281ec54d2cf659640","pDAi2YK0L0QxVJHj",0]]],["Nevada: state",[["Nevada Department of Wildlife","nevada-department-of-wildlife-data-hub-ndow.hub.arcgis.com","","RyxlXSfFi87rAosq",0]]],["Nevada: cities and counties",[["Las Vegas","opendataportal-lasvegas.opendata.arcgis.com","b966d215cd7a4c6caf2132e8ed6ce1fc","F1v0ufATbBQScMtY",0],["Reno","data-cityofreno.opendata.arcgis.com","55a2a7fb3b6342129c6c32278f5e5d40","RjM4BJrv5ZkqP4XC",0]]],["New Hampshire: state",[["NH GRANIT","www.nhgeodata.unh.edu","9077b6cdf1d94589b79cc66d8f919da2","wnvDDrXX8EouLkZP",0],["NHDES Open Data","nh-department-of-environmental-services-open-data-nhdes.hub.arcgis.com","064f2977deae40479c35e7714e5ad911","MAcUimSes4gPY4sM",0]]],["New Jersey: state",[["NJ Office of GIS","njogis-newjersey.opendata.arcgis.com","2156642a93584c6b8eec0498fdd73e76","XVOqAjTOJ5P6ngMu",0],["NJDEP Open Data","gisdata-njdep.opendata.arcgis.com","98aeb9942e774894adeb9a29f62482af","QWdNfRs7lkPq4g4Q",0]]],["New Mexico: state",[["New Mexico Environment Department","data-nmenv.opendata.arcgis.com","","sqciGhV7WvGQn4ky",0],["NM Office of the State Engineer","geospatialdata-ose.opendata.arcgis.com","a9eb3957cd6a44cf9e1f8900476c8db6","qXZbWTdPDbTjl7Dy",0]]],["New York: state",[["NYS GIS Clearinghouse","data.gis.ny.gov","ddc8b98612774f8ea9c8b718ddd576bc","EbVsqZ18sv1kVJ3k",0]]],["New York: cities and counties",[["Buffalo","data.buffalony.gov","","",1],["New York City","data.cityofnewyork.us","","",1],["Rochester","data.cityofrochester.gov","273dc226904e43f0a83baecf54a31397","yoz1ZtATTCokO9nU",0],["Suffolk County","opendata.suffolkcountyny.gov","57f3191192114c32a0e22586cb257278","JsDD4qdG5r2a7hR5",0],["Syracuse","data.syr.gov","86710986bc1842389faaa1c17fe654cf","bdPqSfflsdgFRVVM",0],["Westchester County","gis.westchestercountyny.gov","606726bec1944726a4c505503445a5c3","XKEHpOulfycN9cGC",0]]],["North Carolina: state",[["NC OneMap","www.nconemap.gov","33650305fdf24a1bb46465e4bc598e93","mSDBiLWaIfH92NqI",0]]],["North Carolina: cities and counties",[["Charlotte","data.charlottenc.gov","5d8ea37690104b94b358119129487e47","9Nl857LBlQVyzq54",0],["Durham","live-durhamnc.opendata.arcgis.com","8a5ccf6bcfad4c81beab417e8577b26b","G5vR3cOjh6g2Ed8E",0],["Greensboro","data.greensboro-nc.gov","88aa78a3f03f470f8adb6e03072dcaaa","A7KFW0gHh8qBaXk3",0],["Raleigh","data-ral.opendata.arcgis.com","9afa0ba9c92f4cf6b0eb4356e40423ab","v400IkDOw1ad7Yad",0],["Wake County","data-wake.opendata.arcgis.com","8e6dd38a07da45cd984b1cd29930a81c","a7CWfuGP5ZnLYE7I",0]]],["North Dakota: state",[["North Dakota GIS Hub","gishubdata-ndgov.hub.arcgis.com","c505dcbdc54d429a86c81d859393fc4b","GOcSXpzwBHyk2nog",0]]],["Ohio: state",[["Ohio OGRIP","ogriphome-geohio.hub.arcgis.com","","MlJ0G8iWUyC7jAmu",0],["Ohio DNR","gis-odnr.opendata.arcgis.com","","ajRlmtxbNBjZggOT",0]]],["Ohio: cities and counties",[["Cleveland","data.clevelandohio.gov","a643b07bea7143f393679ed7dc9554e4","dty2kHktVXHrqO8i",0],["Columbus","opendata.columbus.gov","0a37e4488b1f405eb0ea052607047b60","9yy6msODkIBzkUXU",0],["Cuyahoga County","geospatial.gis.cuyahogacounty.gov","4f3cc376f3734fde9031e5ef7481c7de","GXM8JipKyc0m6HBi",0],["Toledo","data.toledo.gov","f3a8acb5f2fc4f3a92fde0fd04dad2f5","2snQ88YUjP9CNEbe",0]]],["Oklahoma: state",[["Oklahoma Open Data","oklahoma-open-data-oklahoma.hub.arcgis.com","","AFMO17kGL5gMkuoK",0]]],["Oklahoma: cities and counties",[["Oklahoma City","data.okc.gov","de916683e3f345df9df48a455c5f9d0b","2mOVdIcRtNH2JsSF",0],["Tulsa","gis2-cityoftulsa.opendata.arcgis.com","49f5fe956376420ab114b0ed70c5e826","XkZ90iCdbTJ9oNXl",0]]],["Oregon: state",[["Oregon GEOHub","geohub.oregon.gov","fefc7dd6e26f481b8892d3b7dd58636c","8PAo5HGmvRMlF2eU",0]]],["Oregon: cities and counties",[["Jackson County","gis-jcgis.opendata.arcgis.com","09be49da318c4bb89f0f0bd7f87205d1","DwYBkWQPdaJNWrPG",0],["Oregon Metro (Portland region)","rlisdiscovery.oregonmetro.gov","9d88a36ba6d44751ae38c60707269eec","McQ0OlIABe29rJJy",0],["Portland","gis-pdx.opendata.arcgis.com","2bd881f893fe47b9bf44bbd6d22ce2b2","quVN97tn06YNGj9s",0]]],["Pennsylvania: state",[["PennShare","data-pennshare.opendata.arcgis.com","","jOy9iZUXBy03ojXb",0],["PA DCNR","newdata-dcnr.opendata.arcgis.com","a32a6666b76f4b1eb55fc21a8a9854e8","CPq7UDkBXVRqtgLR",0]]],["Pennsylvania: cities and counties",[["Philadelphia","data-phl.opendata.arcgis.com","80ecb6974200435f8e4b5696b11ca2b8","fLeGjb7u4uXqeF9q",0],["Pittsburgh","pghgishub-pittsburghpa.opendata.arcgis.com","4a9d0380ac4a4627b9abafdff5342434","YZCmUqbcsUpOKfj7",0]]],["Rhode Island: state",[["RIGIS","www.rigis.org","603e02ff72e346959946d4e2103e3257","S8zZg9pg23JUEexQ",0]]],["Rhode Island: cities and counties",[["Providence GIS","providence-gis-hub-pvdgis.hub.arcgis.com","759e60c6c41c4fe3aa8f27aa8e55ef62","wv9mHoqblhTsnqdG",0],["Providence Open Data","data.providenceri.gov","","",1]]],["South Carolina: state",[["SC Department of Natural Resources","data-scdnr.opendata.arcgis.com","","acgZYxoN5Oj8pDLa",0]]],["South Carolina: cities and counties",[["Charleston County","charleston-county-gis-chascogis.hub.arcgis.com","b96c970103654cd082d5f126daff4f30","jR9eNCjAkxwH2nLe",0]]],["South Dakota: state",[["State of South Dakota","gis-south-dakota-open-data-hub-sdbit.hub.arcgis.com","","PwrabBhZHUggYYSp",0]]],["Tennessee: state",[["Tennessee Downloadable GIS Data","geodata.tn.gov","4649b629c9b647a8822b052cadc89072","YuVBSS7Y1of2Qud1",0]]],["Tennessee: cities and counties",[["Memphis","memphis-open-data-hub-memegis.hub.arcgis.com","fb4f65e9707e4bb2b1e503f140938880","saWmpKJIUAjyyNVc",0],["Nashville","data.nashville.gov","57dd8b686ef0408998f719669b95d629","HdTo6HJqh92wn4D8",0]]],["Texas: state",[["TxDOT Open Data","gis-txdot.opendata.arcgis.com","","KTcxiTD9dsQw4r7Z",0]]],["Texas: cities and counties",[["Austin","data.austintexas.gov","","",1],["Bexar County","gis-bexar.opendata.arcgis.com","03bd1f8488e249df8ebbf9580ed8d21a","8onVmslF2KXErTHT",0],["Corpus Christi","gis-corpus.opendata.arcgis.com","0e6f8151eceb437c856e4bc3cf920227","0J4ZNc4NaTguvRy0",0],["Dallas County","dallas-county-open-data-hub-dallascountygis.hub.arcgis.com","8c9f415c80084ea5ab5bf454173a09af","zqe2kwz79KUqUvxC",0],["Dallas GIS","egisdata-dallasgis.hub.arcgis.com","7cc3ddb4800e436f8ba771ea523b5ddc","rwnOSbfKSwyTBcwN",0],["Dallas Open Data","www.dallasopendata.com","","",1],["El Paso","opendata.elpasotexas.gov","4bd6c73d119a4350897641f8d8a61a2a","hyTVSIhR7dHyDsJF",0],["Fort Worth","data.fortworthtexas.gov","365a6ab74e0448db93c6ecddbb6514bb","3ddLCBXe1bRt7mzj",0],["Harris County","geo-harriscounty.opendata.arcgis.com","17abd25f5caf4befb06005c691007e02","su8ic9KbA7PYVxPS",0],["Houston","cohgis-mycity.opendata.arcgis.com","0330146b830f4487a89ff170e62a8878","NummVBqZSIJKUeVR",0],["San Antonio","opendata-cosagis.opendata.arcgis.com","11dea7e722da42a1a6a6407a8c3ff4be","g1fRTDLeMgspWrYp",0],["Tarrant County","data-tarrantcounty.opendata.arcgis.com","07dd6150f130406ea6bb68ab2b7f98f7","KgTkwJ7lfG2eHF3z",0],["Travis County","tnr-traviscountytx.hub.arcgis.com","2eff5d073fca4eeb97d600cda4699e46","HGcSYZ5bvjRswoCb",0]]],["Utah: state",[["Utah SGID Open Data","opendata.gis.utah.gov","84e1fcc2b93041348ef4329f532ab846","99lidPhWCzftIe9K",0]]],["Utah: cities and counties",[["Salt Lake City","gis-slcgov.opendata.arcgis.com","5db27243a95d4f8099aba0470f9f1f6d","mMBpeYj0vPFotzbe",0],["Salt Lake County","gisdata-slco.opendata.arcgis.com","40cc6e95079f4f7ebcc01635e7f344f7","DJP723NX3ukQ2LtF",0]]],["Vermont: state",[["Vermont Open Geodata Portal","geodata.vermont.gov","0ce1e35a117849fdb89822c80ebff64f","BkFxaEFNwHqX3tAw",0]]],["Virginia: state",[["VGIN Clearinghouse","vgin.vdem.virginia.gov","ab1346979ba544c99dae2ec54ba7e1cd","WNJF1HhUVAm3jccO",0]]],["Virginia: cities and counties",[["Arlington County","gisdata-arlgis.opendata.arcgis.com","3248008859c34cfaa7cac22f1273fdd3","JrtUzVcH8S2wnzVH",0],["Chesapeake","public-chesva.opendata.arcgis.com","3c358a52954e4baea8723c2d842e5784","OAphVRUvJVpBRovs",0],["Fairfax County","data-fairfaxcountygis.opendata.arcgis.com","f8be7fd5a7a4462891868cbfe4a1aa6d","ioennV6PpG5Xodq0",0],["Loudoun County","geohub-loudoungis.opendata.arcgis.com","7310fc278f624a06bd2226f137da963b","MxjRokvPm7bjslyR",0],["Norfolk","data.norfolk.gov","","",1],["Richmond","data.richmondgov.com","","",1],["Virginia Beach","gis.data.vbgov.com","d12298bf52cd4f389051844e9a66d629","CyVvlIiUfRBmMQuu",0]]],["Washington: state",[["Washington Geospatial Open Data","geo.wa.gov","6a33438d424a4009bc5526a1eb9d3a37","jsIt88o09Q0r1j8h",0],["WSDOT Open Data","gisdata-wsdot.opendata.arcgis.com","9a2bfc0592d442258c299b98b1991d27","IYrj3otxNjPsrTRD",0]]],["Washington: cities and counties",[["Clark County","hub-clarkcountywa.opendata.arcgis.com","805517b5067a46c380ea4c4f64e55cc8","ylxwjFBdCPBzP16d",0],["King County GIS","gis-kingcounty.opendata.arcgis.com","d334817cbde1483292c219421e32da9c","Ej0PsM5Aw677QF1W",0],["King County Open Data","data.kingcounty.gov","","",1],["Pierce County","gisdata-piercecowa.opendata.arcgis.com","34f7b1740f7f4806a7f1352d371d5bfa","1UvBaQ5y1ubjUPmd",0],["Seattle GeoData","data-seattlecitygis.opendata.arcgis.com","334a4a5204ba4b3dac75109352611677","ZOyb2t4B0UYuYNYH",0],["Seattle Open Data","data.seattle.gov","","",1],["Snohomish County","snohomish-county-open-data-portal-snoco-gis.hub.arcgis.com","ddea1d4950c44f86bcc9efff71aaf02d","z6WYi9VRHfgwgtyW",0],["Spokane","data-spokane.opendata.arcgis.com","a741c4955dd147b195c49e3e30ab78cb","3PDwyTturHqnGCu0",0],["Tacoma","data.tacoma.gov","28cb0ea3b4a6406d99366c4f4ae52dd0","SCwJH1pD8WSn5T5y",0]]],["West Virginia: state",[["WV GTI Map & Data Portal","data-wvdot.opendata.arcgis.com","","xLpB90lOmCXYDAWo",0]]],["Wisconsin: state",[["Wisconsin DNR Open Data","data-wi-dnr.opendata.arcgis.com","c59132cd84314f3a9e50a2958e6b6b01","Ul9AyFFeFTjf08DW",0]]],["Wisconsin: cities and counties",[["Madison","data-cityofmadison.opendata.arcgis.com","067c50f1d3d847e7b7c36c4efa5168cf","lx96Ahunbwmk5g5p",0],["Milwaukee County","data.county.milwaukee.gov","251150da257b4095912cdcaa5038184e","s1wgJQKbKJihhhaT",0]]],["Wyoming: state",[["Wyoming GeoHub","data.geospatialhub.org","4e3957a8ddbd45ccb7149d150ffec3fe","HVjI8GKrRtjcQ4Ry",0]]],["Wyoming: cities and counties",[["Cheyenne-Laramie County","hub.clcgisc.com","45c91db66706494b86519a5cb635c87c","e5t4ywWgRBNUuDeU",0]]]];
  var BIM_FIND_CREDIT='Portal list and searches: GeoLibre (MIT licence)';
  var BIM_FIND_TYPES=['Feature Service','Map Service','GeoJson'];
  var BIM_FIND_GEOM={point:1,multipoint:1,line:1,multiline:1,polygon:1,multipolygon:1,location:1};
  var BIM_FIND_NUM=20;
  var A3D_FIND={portal:'',q:'',near:true,busy:false,res:[],next:0,total:0,err:'',said:'',groups:{},pick:null,pending:null};
  function bimFindPortal(host){
    var g,i,P;
    for(g=0;g<BIM_DATA_PORTALS.length;g++)for(i=0;i<BIM_DATA_PORTALS[g][1].length;i++){
      P=BIM_DATA_PORTALS[g][1][i];
      if(P[1]===host)return {group:BIM_DATA_PORTALS[g][0],name:P[0],host:P[1],site:P[2],org:P[3],socrata:!!P[4]};
    }
    return null;
  }
  /* a first guess from the address found for the site: its city or county, else its state */
  function bimFindGuess(){
    var ad=' '+String((A3D.site&&A3D.site.address)||'').toLowerCase().replace(/[^a-z0-9]+/g,' ')+' ',g,i,G,st,best='',stHost='';
    if(ad.length<3)return '';
    function has(w){return ad.indexOf(' '+String(w).toLowerCase().replace(/[^a-z0-9]+/g,' ').replace(/^ | $/g,'')+' ')>=0;}
    for(g=0;g<BIM_DATA_PORTALS.length;g++){
      G=BIM_DATA_PORTALS[g];st=G[0].split(':')[0];
      if(G[0].indexOf('Federal')===0||!has(st))continue;
      if(/: state$/.test(G[0])){if(!stHost)stHost=G[1][0][1];continue;}
      for(i=0;i<G[1].length;i++)if(!best&&has(G[1][i][0].replace(/^(City|County|Town) of /i,'')))best=G[1][i][1];
    }
    return best||stHost;
  }
  function bimFindCurrent(){
    if(!A3D_FIND.portal){
      var pr={};try{pr=bimLoadUIPanelPrefs()||{};}catch(eP){}
      A3D_FIND.portal=bimFindGuess()||(bimFindPortal(pr.dataPortal)?pr.dataPortal:'');
    }
    return bimFindPortal(A3D_FIND.portal);
  }
  function bimFindSetPortal(host){
    if(host&&!bimFindPortal(host))return false;
    A3D_FIND.portal=host||'';A3D_FIND.res=[];A3D_FIND.next=0;A3D_FIND.total=0;A3D_FIND.err='';A3D_FIND.said='';A3D_FIND.pick=null;
    try{var pr=bimLoadUIPanelPrefs()||{};pr.dataPortal=host||'';bimSaveUIPanelPrefs(pr);}catch(eS){}
    return true;
  }
  /* ArcGIS Online's item search: the words, the types read here, the catalog's groups or the
     organisation, public items only; words that are Lucene syntax are dropped, not escaped */
  function bimHubText(q){
    return String(q==null?'':q).replace(/["\\\/(){}\[\]\^~:!?+]|&&|\|\|/g,' ').replace(/\b(?:AND|OR|NOT)\b/gi,' ').replace(/\s+/g,' ').replace(/^ | $/g,'');
  }
  function bimHubSearchUrl(q,o){
    var text=bimHubText(q),i,ty=[],gr=[];
    for(i=0;i<BIM_FIND_TYPES.length;i++)ty.push('type:"'+BIM_FIND_TYPES[i]+'"');
    for(i=0;o.groups&&i<o.groups.length;i++)if(/^[0-9a-f]{32}$/i.test(o.groups[i]))gr.push('group:'+o.groups[i]);
    var qq=(text?'('+text+') AND ':'')+'('+ty.join(' OR ')+')'+(gr.length?' AND ('+gr.join(' OR ')+')':'')+
      (!gr.length&&o.org&&/^[0-9A-Za-z]{16}$/.test(o.org)?' AND orgid:'+o.org:'')+' AND access:public';
    return 'https://www.arcgis.com/sharing/rest/search?q='+encodeURIComponent(qq)+'&f=json&start='+(o.start||1)+'&num='+(o.num||BIM_FIND_NUM)+
      '&sortField='+(text?'relevance':'title')+'&sortOrder='+(text?'desc':'asc')+
      (o.bbox?'&bbox='+o.bbox.map(function(v){return v.toFixed(5);}).join(','):'');
  }
  /* a Hub site's catalog is the groups its site item names (catalogV2 on current sites, catalog on older) */
  function bimHubGroups(js){
    var out=[],seen={},i,j,f,p;
    function add(v){
      if(typeof v==='string'){if(/^[0-9a-f]{32}$/i.test(v)&&!seen[v]){seen[v]=1;out.push(v);}return;}
      if(Array.isArray(v)){for(var k=0;k<v.length;k++)add(v[k]);return;}
      if(v&&typeof v==='object'){add(v.any);add(v.all);}
    }
    f=js&&js.catalogV2&&js.catalogV2.scopes&&js.catalogV2.scopes.item&&js.catalogV2.scopes.item.filters;
    if(Array.isArray(f))for(i=0;i<f.length;i++){p=f[i]&&f[i].predicates;if(Array.isArray(p))for(j=0;j<p.length;j++)add(p[j]&&p[j].group);}
    if(!out.length&&js&&js.catalog)add(js.catalog.groups);
    return out;
  }
  function bimHubSiteGroups(site){
    if(!site)return Promise.resolve([]);
    if(A3D_FIND.groups[site])return Promise.resolve(A3D_FIND.groups[site]);
    return fetch('https://www.arcgis.com/sharing/rest/content/items/'+site+'/data?f=json').then(function(r){
      if(!r.ok)throw {http:r.status};return r.json();
    }).then(function(js){var g=bimHubGroups(js);A3D_FIND.groups[site]=g;return g;},function(){return [];});   /* the organisation is the fallback */
  }
  function bimSocrataSearchUrl(dom,q,offset){
    var text=String(q==null?'':q).replace(/^\s+|\s+$/g,'');
    return 'https://api.us.socrata.com/api/catalog/v1?search_context='+encodeURIComponent(dom)+'&domains='+encodeURIComponent(dom)+'&only=dataset'+
      (text?'&q='+encodeURIComponent(text):'&order=name')+'&offset='+offset+'&limit=100';
  }
  /* one catalog entry as a result, if it is a spatial dataset of this portal; the addresses are
     built from the portal's own host, never taken from the answer */
  function bimSocrataItem(en,dom){
    var r=en&&en.resource,id=r&&String(r.id||'').toLowerCase(),ty,fn,i,geom='';
    if(!r||!/^[a-z0-9]{4}-[a-z0-9]{4}$/.test(id))return null;
    if(!en.metadata||en.metadata.domain!==dom)return null;
    ty=Array.isArray(r.columns_datatype)?r.columns_datatype:[];fn=Array.isArray(r.columns_field_name)?r.columns_field_name:[];
    for(i=0;i<ty.length;i++)if(typeof ty[i]==='string'&&BIM_FIND_GEOM[ty[i].toLowerCase()]){geom=String(fn[i]||'');break;}
    if(i>=ty.length)return null;
    if(!/^[A-Za-z_][A-Za-z0-9_]*$/.test(geom))geom='';
    return {src:'socrata',id:id,title:String(r.name||id).slice(0,120),type:'Socrata dataset',
      owner:String((en.classification&&en.classification.domain_category)||r.attribution||dom).slice(0,80),
      snippet:String(r.description||'').slice(0,200),data:'https://'+dom+'/resource/'+id+'.geojson',geom:geom,page:'https://'+dom+'/d/'+id};
  }
  function bimHubItem(it){
    if(!it||!/^[0-9a-f]{32}$/i.test(String(it.id||'')))return null;
    return {src:'hub',id:it.id,title:String(it.title||it.id).slice(0,120),type:String(it.type||''),owner:String(it.owner||'').slice(0,80),
      snippet:String(it.snippet||'').slice(0,200),url:String(it.url||''),page:'https://www.arcgis.com/home/item.html?id='+it.id};
  }
  /* one press, one search; More continues it */
  function bimFindSearch(q,more){
    var P=bimFindCurrent(),a,start;
    if(!P){a3dToast('Pick a portal to search: a city, county, state or federal agency');return null;}
    if(A3D_FIND.busy){a3dToast('A search is already on its way');return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot search');return null;}
    if(!more){A3D_FIND.q=String(q==null?A3D_FIND.q:q).replace(/^\s+|\s+$/g,'').slice(0,120);A3D_FIND.res=[];A3D_FIND.next=0;A3D_FIND.pick=null;}
    else if(!A3D_FIND.next)return null;
    start=more?A3D_FIND.next:1;
    a=A3D_FIND.near?bimCtxArea():null;
    A3D_FIND.busy=true;A3D_FIND.err='';A3D_FIND.said='searching '+P.name+' ...';
    refreshProps();
    var host=P.socrata?'api.us.socrata.com':'www.arcgis.com',p;
    function fin(){A3D_FIND.busy=false;refreshProps();}
    if(P.socrata){
      var got=[],off=start-1,total=0,b=0;
      p=(function batch(){
        return fetch(bimSocrataSearchUrl(P.host,A3D_FIND.q,off)).then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
          var js,i,it;
          try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
          if(js.error)throw {said:String(js.error).slice(0,160)};
          if(!Array.isArray(js.results))throw {bad:true};
          total=js.resultSetSize||0;
          for(i=0;i<js.results.length;i++){it=bimSocrataItem(js.results[i],P.host);if(it)got.push(it);}
          off+=js.results.length;b++;
          if(!js.results.length||off>=total)return 0;
          if(got.length<BIM_FIND_NUM&&b<5)return batch();
          return off+1;
        });
      })().then(function(next){return {items:got,next:next,total:total};});
    }else{
      p=bimHubSiteGroups(P.site).then(function(gr){
        return fetch(bimHubSearchUrl(A3D_FIND.q,{groups:gr,org:P.org,start:start,bbox:a?[a.w,a.s,a.e,a.n]:null}));
      }).then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
        var js,i,it,out=[];
        try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
        if(js.error)throw {said:String(js.error.message||'an error').slice(0,160)};
        if(!Array.isArray(js.results))throw {bad:true};
        for(i=0;i<js.results.length;i++){it=bimHubItem(js.results[i]);if(it)out.push(it);}
        return {items:out,next:js.nextStart>0?js.nextStart:0,total:js.total||0};
      });
    }
    p=p.then(function(r){
      A3D_FIND.res=A3D_FIND.res.concat(r.items);A3D_FIND.next=r.next;A3D_FIND.total=r.total;
      A3D_FIND.said=A3D_FIND.res.length?(A3D_FIND.res.length+' found'+(r.next?', more to see':'')):
        ('nothing found'+(a&&!P.socrata?' near the site: untick Near the site to search the whole portal':''));
      fin();
      return {count:A3D_FIND.res.length,next:r.next};
    },function(e){
      A3D_FIND.err=e&&e.said?host+' said: '+e.said:bimCtxErr(host,e);A3D_FIND.said='';
      fin();a3dToast('Search: '+A3D_FIND.err);
      return {error:A3D_FIND.err};
    });
    A3D_FIND.pending=p;
    return p;
  }
  /* is a result already a data layer? */
  function bimFindAdded(it){
    var L=bimDataList(),i,u=it.src==='socrata'?it.data:it.type==='GeoJson'?bimFindItemData(it.id):String(it.url||'').replace(/\/+$/,'');
    for(i=0;i<L.length;i++)if(u&&(L[i].url===u||L[i].url.indexOf(u+'/')===0))return true;
    return false;
  }
  function bimFindItemData(id){return 'https://www.arcgis.com/sharing/rest/content/items/'+id+'/data';}
  function bimFindCreditFor(){var P=bimFindCurrent();return P?P.name+' open data ('+P.host+')':'';}
  /* a result becomes a V134 data layer; a whole service lists its feature layers to pick from */
  function bimFindAdd(ix,layer){
    var it=A3D_FIND.res[ix],u,cr=bimFindCreditFor(),m;
    if(!it)return null;
    if(it.src==='socrata')return Promise.resolve(bimDataAdd(it.data,it.title,null,cr,{geom:it.geom}));
    if(it.type==='GeoJson')return Promise.resolve(bimDataAdd(bimFindItemData(it.id),it.title,null,cr));
    u=String(it.url||'').split('?')[0].replace(/\/+$/,'');
    if(layer!=null)return Promise.resolve(bimDataAdd(u+'/'+layer.id,(it.title+' - '+layer.name).slice(0,60),null,cr));
    if(/\/(FeatureServer|MapServer)\/\d+$/i.test(u))return Promise.resolve(bimDataAdd(u,it.title,null,cr));
    if(!/^https:\/\/\S+\/(FeatureServer|MapServer)$/i.test(u)){a3dToast(it.title+' has no ArcGIS layer address to read');return Promise.resolve(null);}
    var host=bimMapHost(u);
    a3dToast('Reading the layers of '+it.title+' ...');
    return fetch(u+'?f=json').then(function(r){if(!r.ok)throw {http:r.status};return r.text();}).then(function(tx){
      var js,i,ls=[],l;
      try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
      if(js.error)throw {said:String(js.error.message||'an error').slice(0,160)};
      for(i=0;Array.isArray(js.layers)&&i<js.layers.length;i++){
        l=js.layers[i];
        if(l&&typeof l.id==='number'&&isFinite(l.id)&&!l.subLayerIds&&(!l.type||/feature layer/i.test(l.type)))ls.push({id:l.id,name:String(l.name||('Layer '+l.id)).slice(0,60)});
      }
      if(!ls.length){a3dToast(it.title+': '+host+' lists no feature layers (it may be imagery)');return null;}
      if(ls.length===1)return bimDataAdd(u+'/'+ls[0].id,it.title,null,cr);
      A3D_FIND.pick={ix:ix,layers:ls};refreshProps();
      a3dToast(it.title+' holds '+ls.length+' layers: pick the ones to add');
      return {pick:ls.length};
    }).then(null,function(e){
      var msg=e&&e.said?host+' said: '+e.said:bimCtxErr(host,e);
      a3dToast(it.title+': '+msg);
      return {error:msg};
    });
  }
  /* a layer added is one undo step, and fetched at once */
  function bimDataAdd(url,name,color,credit,extra){
    var u=String(url==null?'':url).replace(/^\s+|\s+$/g,''),k=bimDataKind(u),L=bimDataList(),i,lyr;
    if(k.error){a3dToast(k.error);return null;}
    for(i=0;i<L.length;i++)if(L[i].url===u){a3dToast('That layer is here already: '+L[i].name);return null;}
    pushUndo();
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    if(!Array.isArray(A3D.site.dataLayers))A3D.site.dataLayers=[];
    lyr={id:'data-'+Date.now().toString(36)+'-'+(A3D.seq++),name:String(name||bimDataNameFromUrl(u)).slice(0,60),kind:k.kind,url:u,
      color:/^#[0-9a-fA-F]{6}$/.test(color||'')?color.toLowerCase():BIM_SCHEME_COLS[A3D.site.dataLayers.length%BIM_SCHEME_COLS.length],
      visible:true,credit:String(credit||bimMapHost(u)).slice(0,160)};
    if(extra&&/^[A-Za-z_][A-Za-z0-9_]*$/.test(extra.geom||''))lyr.geom=extra.geom;   /* __acad3dV135: a Socrata dataset's geometry column */
    A3D.site.dataLayers.push(lyr);
    refreshProps();saveSoon();bimLayersPanelRefresh();   /* __acad3dV148 */
    if(bimCtxArea())bimDataFetch(lyr.id);
    else a3dToast(lyr.name+' added: set the site latitude and longitude, then Refresh it');
    return lyr.id;
  }
  function bimDataRemove(id){
    var L=bimDataList(),i;
    for(i=0;i<L.length;i++)if(L[i].id===id)break;
    if(i>=L.length)return false;
    pushUndo();
    var nm=L[i].name;
    L.splice(i,1);
    /* its features stay stored, so an undo brings the layer back whole; a load drops orphans */
    delete A3D_DATA.cache[id];
    if(A3D_DATA.sel&&A3D_DATA.sel.layer===id)A3D_DATA.sel=null;
    refreshProps();paint();saveSoon();bimLayersPanelRefresh();   /* __acad3dV148 */
    a3dToast(nm+' removed');
    return true;
  }
  function bimDataSet(id,field,val){
    var L=bimDataById(id),v;
    if(!L)return false;
    if(field==='visible'){v=!!val&&val!=='false';if(L.visible===v)return true;}
    else if(field==='name'){v=String(val==null?'':val).replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,60);if(!v){a3dToast('A data layer needs a name');refreshProps();return false;}}
    else if(field==='color'){v=String(val||'');if(!/^#[0-9a-fA-F]{6}$/.test(v)){a3dToast('That is not a colour');refreshProps();return false;}v=v.toLowerCase();}
    else if(field==='by'){v=String(val==null?'':val).slice(0,80);if(v&&bimDataAttrKeys(id).indexOf(v)<0){a3dToast(L.name+' has no attribute '+v);refreshProps();return false;}}   /* __acad3dV136 */
    else if(field==='opacity'){v=parseFloat(val);if(!isFinite(v)){a3dToast('Opacity is a percentage, 10 to 100');refreshProps();return false;}v=Math.max(0.1,Math.min(1,v>1?v/100:v));v=Math.round(v*100)/100;}
    else return false;
    if(L[field]===v||(field==='by'&&!v&&!L.by))return true;
    pushUndo();
    L[field]=v;
    if(field==='visible'&&!v&&A3D_DATA.sel&&A3D_DATA.sel.layer===id)A3D_DATA.sel=null;
    refreshProps();paint();saveSoon();bimLayersPanelRefresh();   /* __acad3dV148 */
    return true;
  }
  function bimDataOpacity(L){var v=L.opacity;return typeof v==='number'&&v>=0.1&&v<=1?v:1;}   /* __acad3dV136 */
  /* a layer's features in model terms, kept until the site's place, true north or the features change */
  function bimDataModel(L){
    var org=bimMapOrigin(),F=bimDataFeats(L.id),key,c;
    if(!org)return null;
    key=org.lat+','+org.lon+','+bimTrueNorthDeg();
    c=A3D_DATA.cache[L.id];
    if(c&&c.key===key&&c.F===F)return c;
    c={key:key,F:F,feats:[]};
    F.forEach(function(f,fi){
      var x={fi:fi,rings:[],lines:[],points:[],area:0};
      bimGeoParts(f.g).forEach(function(pp){
        var pt=bimGeoPositions(pp.pts),m;
        if(!pt)return;
        m=pt.map(function(q){return bimGeoToModel(q[0],q[1],org);});
        if(pp.kind==='ring'){
          if(m.length>1&&m[0][0]===m[m.length-1][0]&&m[0][1]===m[m.length-1][1])m.pop();
          if(m.length>=3){x.rings.push({pts:m,hole:!!pp.hole});x.area+=(pp.hole?-1:1)*bimPolyArea(m);}
        }else if(pp.kind==='line'){if(m.length>=2)x.lines.push(m);}
        else if(pp.kind==='point')x.points.push(m[0]);
      });
      c.feats.push(x);
    });
    A3D_DATA.cache[L.id]=c;
    return c;
  }
  /* on the plan, under the model's linework: never on paper */
  function drawDataLayers(ctx,V,W,H){
    A3D.lastDataDrawn=0;
    if(A3D.sheetCapture||A3D_PLOT.on)return;
    var L=bimDataList(),y=bimShadowGround(),i,j,c,f,sel,n=0;
    function S(p){return toScreen([p[0],y,p[1]],V,W,H);}
    function path(pts,close){
      var p=S(pts[0]),k;
      ctx.moveTo(p[0],p[1]);
      for(k=1;k<pts.length;k++){p=S(pts[k]);ctx.lineTo(p[0],p[1]);}
      if(close)ctx.closePath();
    }
    for(i=0;i<L.length;i++){
      if(!L[i].visible)continue;
      c=bimDataModel(L[i]);
      if(!c)continue;
      ctx.save();
      ctx.strokeStyle=L[i].color;ctx.fillStyle=L[i].color;
      var ds=bimDataLensScale(L[i]),op=bimDataOpacity(L[i]),fa=ds?0.5:0.16,fc;   /* __acad3dV136: by an attribute, at an opacity */
      ctx.globalAlpha=op;
      for(j=0;j<c.feats.length;j++){
        f=c.feats[j];
        if(ds){fc=bimDataFeatCol(L[i],ds,f.fi);ctx.strokeStyle=fc;ctx.fillStyle=fc;}
        sel=!!(A3D_DATA.sel&&A3D_DATA.sel.layer===L[i].id&&A3D_DATA.sel.fi===f.fi);
        ctx.lineWidth=sel?2.6:1.2;
        if(f.rings.length){
          ctx.beginPath();
          f.rings.forEach(function(r){path(r.pts,true);});
          ctx.globalAlpha=(sel?Math.min(1,fa*2.1):fa)*op;ctx.fill('evenodd');ctx.globalAlpha=op;ctx.stroke();
        }
        if(f.lines.length){ctx.beginPath();f.lines.forEach(function(l){path(l,false);});ctx.stroke();}
        f.points.forEach(function(q){var p=S(q);ctx.beginPath();ctx.arc(p[0],p[1],sel?5:3.5,0,Math.PI*2);ctx.fill();});
        n++;
      }
      ctx.restore();
    }
    A3D.lastDataDrawn=n;
  }
  /* what data is under a screen point: a point, then a line, then the smallest area; later layers first */
  function bimDataPick(sx,sy){
    var L=bimDataList(),y=bimShadowGround(),g=groundPoint(sx,sy,y),P,tol,i,j,k,c,f,best=null,bestA=Infinity,pass,inside;
    if(!g)return null;
    P=[g[0],g[2]];
    tol=6*Math.max(A3D.cam.dist,0.5)/(Math.max(1,cvH())*1.2);
    for(pass=0;pass<3;pass++){
      for(i=L.length-1;i>=0;i--){
        if(!L[i].visible)continue;
        c=bimDataModel(L[i]);
        if(!c)continue;
        for(j=c.feats.length-1;j>=0;j--){
          f=c.feats[j];
          if(pass===0){
            for(k=0;k<f.points.length;k++)if(Math.hypot(f.points[k][0]-P[0],f.points[k][1]-P[1])<=tol)return {layer:L[i].id,fi:f.fi};
          }else if(pass===1){
            for(k=0;k<f.lines.length;k++){
              var l=f.lines[k],m;
              for(m=0;m+1<l.length;m++)if(bimPointSegDist(P[0],P[1],l[m][0],l[m][1],l[m+1][0],l[m+1][1])<=tol)return {layer:L[i].id,fi:f.fi};
            }
          }else if(f.rings.length){
            inside=0;
            for(k=0;k<f.rings.length;k++)if(bimPointInPoly(P,f.rings[k].pts))inside++;
            if(inside%2===1&&f.area<bestA){bestA=f.area;best={layer:L[i].id,fi:f.fi};}
          }
        }
      }
    }
    return best;
  }
  /* the picked area's largest outer ring as a property line: one undo step */
  function bimDataToProperty(){
    var s=A3D_DATA.sel,L=s?bimDataById(s.layer):null,c=L?bimDataModel(L):null,f=null,outer=null,i,legs,pr;
    if(c)for(i=0;i<c.feats.length;i++)if(c.feats[i].fi===s.fi)f=c.feats[i];
    if(!f||!f.rings.length){a3dToast('Pick an area, such as a parcel, to make a property line from');return null;}
    f.rings.forEach(function(r){if(!r.hole&&(!outer||bimPolyArea(r.pts)>bimPolyArea(outer)))outer=r.pts;});
    if(!outer){a3dToast('That area has no outer ring');return null;}
    legs=bimLegsFromRing(outer);
    if(legs.length<3){a3dToast('That area has fewer than 3 sides');return null;}
    pushUndo();
    pr=bimNewProperty(outer[0],legs);
    pr.dataSource={layer:L.name,credit:L.credit,props:JSON.parse(JSON.stringify(bimDataFeats(L.id)[s.fi].p||{}))};
    A3D.objs.push(pr);
    A3D.sel=pr.id;A3D.selSet=[pr.id];A3D_DATA.sel=null;
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(pr.name+' from '+L.name+': '+bimClosureText(bimPropertyGeometry(pr)));
    return pr;
  }
  /* the shown layers' credits, for the line over the viewport */
  function bimDataCreditHtml(){
    var L=bimDataList(),c=[],i;
    for(i=0;i<L.length;i++)if(L[i].visible&&bimDataFeats(L[i].id).length&&c.indexOf(L[i].credit)<0)c.push(L[i].credit);
    return c.length?'Data: '+bimEsc(c.join('; ')):'';
  }
