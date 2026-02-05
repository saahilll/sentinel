package com.sentinel.sentinel_core.model;

import jakarta.persistence.*;
import lombok.Data;
import java.util.UUID;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "tenants")
public class Tenant {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private String name; 
    
    @Column(nullable = false, unique = true)
    private String slug; 

    private LocalDateTime createdAt;

    public Tenant() {
        this.createdAt = LocalDateTime.now();
    }
}