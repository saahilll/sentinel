package com.sentinel.sentinel_core.model;

import jakarta.persistence.*;
import lombok.Data;
import java.util.UUID;

@Data
@Entity
@Table(name = "tenant_members")
public class TenantMember {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    // The User
    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    // The Organization they belong to
    @ManyToOne
    @JoinColumn(name = "tenant_id", nullable = false)
    private Tenant tenant;

    // SECURITY: What can they do? (ADMIN, VIEWER, EDITOR)
    @Column(nullable = false)
    private String role; 
}