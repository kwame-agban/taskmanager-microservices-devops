
@Slf4j
import lombok.extern.slf4j.Slf4j;

[P1] 2825 : PORTAIL - menu aide en ligne et menu catalogue

[messages_fr.properties]
service.indisponible=Le service est actuellement indisponible.


[fragment-service-indisponible.html]
    <div class="col-12">
        <div id="alert" class="alert alert-danger fade show text-center">
            <p th:text="#{service.indisponible}"></p>
        </div>
    </div>
	
	==>(i) dans quelle condition appelle t-on le fragment-service-indisponible.html de squeleton?
	quel est le test effectué avant l'affichage du texte : service.indisponible

[MenuWebResource.java]
        MainMenuDTO menuAssistance = new MainMenuDTOBuilder().idInput("btnAssistance").textLabel("menu.lateral.assistance").idLabel("lblAssistance")
                .addSousMenu(menuAEL).addSousMenu(menuFormation).addSousMenu(menuCatalogue).addSousMenu(menuOutils).addSousMenu(menuDemandeAssist)
                .addSousMenu(menuFAQ).typeMenu("Aide").build();	
				
				
[CataloguesWebResource.java]
	...
	...
    @ModelAttribute("etatService")
    public Boolean getEtatService() {
        boolean etatService = false;

        try {
            if (getServicePortailService().findByLibelle(LIBELLE_SERVICE).getEtatService() == EtatService.DEMARRE)
                etatService = true;
        } catch (ServicePortailNotFoundException e) {
            LOGGER.debug(e.getMessage());
        }

        return etatService;
    }				

[CataloguesWebResourceBase.java]	
	    protected ServicePortailService getServicePortailService() {
        log.info("Ka");
        return servicePortailService;
    }
