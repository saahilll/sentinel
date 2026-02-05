package com.sentinel.sentinel_core.service;

import com.sentinel.sentinel_core.model.Tenant;
import com.sentinel.sentinel_core.repository.TenantRepository;
import org.springframework.stereotype.Service;

@Service
public class TenantService {

    private final TenantRepository tenantRepository;

    public TenantService(TenantRepository tenantRepository) {
        this.tenantRepository = tenantRepository;
    }

    public Tenant createTenant(String companyName) {
        String baseSlug = companyName.toLowerCase()
                                     .replaceAll("[^a-z0-9]", "-") 
                                     .replaceAll("-+", "-")        
                                     .replaceAll("^-|-$", "");     

        String finalSlug = baseSlug;
        int counter = 1;

        while (tenantRepository.existsBySlug(finalSlug)) {
            finalSlug = baseSlug + "-" + counter;
            counter++;
        }
        
        Tenant newTenant = new Tenant();
        newTenant.setName(companyName);
        newTenant.setSlug(finalSlug); 
        
        return tenantRepository.save(newTenant);
    }
}